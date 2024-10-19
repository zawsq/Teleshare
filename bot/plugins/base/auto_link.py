import uuid

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.database import MongoDB
from bot.options import options
from bot.utilities.helpers import DataEncoder, RateLimiter
from bot.utilities.pyrofilters import ConvoMessage, PyroFilters
from bot.utilities.pyrotools import FileResolverModel

database = MongoDB()


@Client.on_message(
    filters.private
    & PyroFilters.admin(allow_global=True)
    & PyroFilters.user_not_in_conversation()
    & (filters.audio | filters.photo | filters.video | filters.document | filters.sticker),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def auto_link_gen(client: Client, message: ConvoMessage) -> Message | None:
    """Handle files that is send or forwarded directly to the bot and generate a link for it."""

    if getattr(client.me, "id", None) == message.from_user.id or not config.AUTO_GENERATE_LINK:
        return None

    file_type = message.document or message.video or message.photo or message.audio or message.sticker
    message_id = message.id

    if options.settings.BACKUP_FILES:
        backup_file = await message.copy(chat_id=config.BACKUP_CHANNEL)
        message_id = backup_file[0].id if isinstance(backup_file, list) else backup_file.id

    unique_link = f"{uuid.uuid4().int}"
    file_link = DataEncoder.encode_data(unique_link)
    file_origin = config.BACKUP_CHANNEL if options.settings.BACKUP_FILES else message.chat.id

    file_data = FileResolverModel(
        caption=message.caption.markdown if message.caption else None,
        file_id=file_type.file_id,
        message_id=message_id,
    )

    add_file = await database.add_file(file_link=file_link, file_origin=file_origin, file_data=[file_data.model_dump()])

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
