from typing import ClassVar

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.database import MongoDB
from bot.utilities.helpers import DataEncoder
from bot.utilities.pyrofilters import ConvoMessage, PyroFilters


class MakeFilesCommand:
    database: MongoDB = MongoDB("Zaws-File-Share")
    files_cache: ClassVar[dict[int, list]] = {}

    @classmethod
    async def handle_convo_start(cls, client: Client, message: ConvoMessage) -> Message:  # noqa: ARG003
        unique_id = message.chat.id + message.from_user.id
        cls.files_cache.setdefault(unique_id, [])
        return await message.reply("Send your files.")

    @classmethod
    async def handle_conversation(cls, client: Client, message: ConvoMessage) -> Message:  # noqa: ARG003
        unique_id = message.chat.id + message.from_user.id
        file_type = message.document or message.video or message.photo or message.audio
        if not file_type:
            return await message.reply(text="> Only send files!", quote=True)

        cls.files_cache[unique_id].append(
            {
                "caption": message.caption.markdown if message.caption else None,
                "file_id": file_type.file_id,
                "file_name": file_type.file_name if hasattr(file_type, "file_name") else file_type.file_unique_id,
                "message_id": message.id,
            },
        )

        file_names = "\n".join(i["file_name"] for i in cls.files_cache[unique_id])
        extra_message = "- Send more documents for batch files.\n- Send /make_link to create a sharable link."
        return await message.reply(text=f"```\nFile(s):\n{file_names}\n```\n{extra_message}", quote=True)

    @classmethod
    async def handle_convo_stop(cls, client: Client, message: ConvoMessage) -> Message:
        unique_id = message.chat.id + message.from_user.id
        user_cache = [i["message_id"] for i in cls.files_cache[unique_id]]

        if not user_cache:
            return await message.reply(text="No file inputs, stopping task.", quote=True)

        forwarded_messages = await client.forward_messages(
            chat_id=config.BACKUP_CHANNEL,
            from_chat_id=message.chat.id,
            message_ids=user_cache,
            hide_sender_name=True,
        )

        files_backup = []
        for msg in forwarded_messages if isinstance(forwarded_messages, list) else [forwarded_messages]:
            file_type = msg.document or msg.video or msg.photo or msg.audio
            files_backup.append(
                {
                    "caption": msg.caption.markdown if msg.caption else None,
                    "file_id": file_type.file_id,
                    "message_id": msg.id,
                },
            )

        file_link = DataEncoder.encode_data(str(message.date))
        file_origin = config.BACKUP_CHANNEL
        await cls.database.update_one(
            collection="Files",
            db_filter={"_id": file_link},
            update={"$set": {"file_origin": file_origin, "files": files_backup}},
        )

        cls.files_cache.pop(unique_id)

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


@Client.on_message(
    filters.private
    & PyroFilters.admin(allow_global=True)
    & PyroFilters.create_conversation_filter(
        convo_start="/make_files",
        convo_stop="/make_link",
    ),
)
async def make_files_command_handler(client: Client, message: ConvoMessage) -> Message | None:
    if message.convo_start:
        return await MakeFilesCommand.handle_convo_start(client=client, message=message)
    if message.conversation:
        return await MakeFilesCommand.handle_conversation(client=client, message=message)
    if message.convo_stop:
        return await MakeFilesCommand.handle_convo_stop(client=client, message=message)
    return None
