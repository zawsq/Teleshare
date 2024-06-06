from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.database import MongoDB
from bot.options import options
from bot.utilities.helpers import DataEncoder, RateLimiter
from bot.utilities.pyrofilters import ConvoMessage, PyroFilters
from bot.utilities.pyrotools import FileResolverModel

database: MongoDB = MongoDB(database=config.MONGO_DB_NAME)


@Client.on_message(
    filters.private
    & PyroFilters.admin(allow_global=True)
    & PyroFilters.user_not_in_conversation()
    & (filters.audio | filters.photo | filters.video | filters.document),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def auto_link_gen(client: Client, message: ConvoMessage) -> Message | None:
    """Handle files that is send or forwarded directly to the bot and generate a link for it."""

    file_type = message.document or message.video or message.photo or message.audio
    message_id = message.id

    if options.settings.BACKUP_FILES:
        backup_file = await message.copy(chat_id=config.BACKUP_CHANNEL)
        message_id = backup_file[0].id if isinstance(backup_file, list) else backup_file.id

    file_link = DataEncoder.encode_data(str(message.date))
    file_origin = config.BACKUP_CHANNEL if options.settings.BACKUP_FILES else message.chat.id

    file_data = FileResolverModel(
        caption=message.caption.markdown if message.caption else None,
        file_id=file_type.file_id,
        message_id=message_id,
    )

    await database.update_one(
        collection="Files",
        db_filter={"_id": file_link},
        update={"$set": {"file_origin": file_origin, "files": [file_data.model_dump()]}},
    )

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
