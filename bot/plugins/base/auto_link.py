import asyncio
import uuid
from datetime import datetime
from typing import ClassVar, TypedDict

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.database import MongoDB
from bot.options import options
from bot.utilities.helpers import DataEncoder, RateLimiter
from bot.utilities.pyrofilters import ConvoMessage, PyroFilters
from bot.utilities.pyrotools import FileResolverModel


class CacheEntry(TypedDict):
    """Cache entry for files."""

    time: datetime
    files: list[dict]


class AutoLinkGen:
    database = MongoDB()
    background_tasks: ClassVar[set[asyncio.Task]] = set()
    files_cache: ClassVar[dict[int, CacheEntry]] = {}

    @classmethod
    async def process_files(
        cls,
        client: Client,
        message: Message,
        file_data: list[dict[str, str | int]],
    ) -> Message:
        "Handles file backups"

        unique_link = f"{uuid.uuid4().int}"
        file_link = DataEncoder.encode_data(unique_link)
        file_origin = config.BACKUP_CHANNEL if options.settings.BACKUP_FILES else message.chat.id

        add_file = await cls.database.add_file(file_link=file_link, file_origin=file_origin, file_data=file_data)

        if add_file:
            link = f"https://t.me/{client.me.username}?start={file_link}"  # type: ignore[reportOptionalMemberAccess]
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Share URL", url=f"https://t.me/share/url?url={link}")]],
            )

            return await message.reply(
                text=f"Here is your link:\n>{link}",
                quote=True,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )

        return await message.reply("Couldn't add files to database")

    @classmethod
    async def media_group_handler(cls, client: Client, message: Message) -> None:
        "backup"
        await asyncio.sleep(3)

        file_datas = cls.files_cache[message.from_user.id][message.media_group_id]

        if options.settings.BACKUP_FILES:
            message_ids = [i["message_ids"] for i in file_datas]
            forwarded_messages = await client.forward_messages(
                chat_id=config.BACKUP_CHANNEL,
                from_chat_id=message.chat.id,
                message_ids=message_ids,
                hide_sender_name=True,
            )

            file_datas: list[dict[str, str]] = []

            for msg in forwarded_messages if isinstance(forwarded_messages, list) else [forwarded_messages]:
                file_type = msg.document or msg.video or msg.photo or msg.audio or msg.sticker

                file_datas.append(
                    (
                        FileResolverModel(
                            caption=msg.caption.markdown if message.caption else None,
                            file_id=file_type.file_id,
                            message_id=msg.id,
                            media_group_id=msg.media_group_id,
                        )
                    ).model_dump(),
                )

        del cls.files_cache[message.from_user.id][message.media_group_id]
        return await cls.process_files(client=client, message=message, file_data=file_datas)

    @classmethod
    async def handle_files(cls, client: Client, message: Message) -> None:
        file_type = message.document or message.video or message.photo or message.audio or message.sticker
        message_id = message.id
        user_id = message.from_user.id

        resolve_file = FileResolverModel(
            caption=message.caption.markdown if message.caption else None,
            file_id=file_type.file_id,
            message_id=message_id,
        )

        if message.media_group_id:
            if not cls.files_cache.get(user_id, {}).get(message.media_group_id):
                cls.files_cache[user_id] = {message.media_group_id: []}
                task = asyncio.create_task(cls.media_group_handler(client=client, message=message))
                cls.background_tasks.add(task)
                task.add_done_callback(cls.background_tasks.discard)

            resolve_file.media_group_id = message.media_group_id
            cls.files_cache[user_id][message.media_group_id].append((resolve_file).model_dump())
        else:
            if options.settings.BACKUP_FILES:
                backup_file = await message.copy(chat_id=config.BACKUP_CHANNEL)
                resolve_file.message_id = backup_file[0].id if isinstance(backup_file, list) else backup_file.id

            await cls.process_files(client=client, message=message, file_data=[resolve_file.model_dump()])



@Client.on_message(
    filters.private
    & PyroFilters.admin(allow_global=True)
    & PyroFilters.subscription()
    & PyroFilters.user_not_in_conversation()
    & (filters.audio | filters.photo | filters.video | filters.document | filters.sticker),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def auto_link_gen(client: Client, message: ConvoMessage) -> Message | None:
    """Handle files that is send or forwarded directly to the bot and generate a link for it."""

    if getattr(client.me, "id", None) == message.from_user.id or not config.AUTO_GENERATE_LINK:
        return None

    await AutoLinkGen.handle_files(client=client, message=message)
