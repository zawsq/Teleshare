import binascii

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.errors import MessageIdInvalid
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.database import MongoDB
from bot.database.models import FltId, UpdSet
from bot.options import options
from bot.utilities.helpers import Encoding
from bot.utilities.pyrofilters import PyroFilters
from bot.utilities.schedule_manager import schedule_manager

database = MongoDB("Zaws-File-Share")


@Client.on_message(
    filters.command("start") & filters.private & PyroFilters.subscription(),
    group=0,
)
async def file_start(
    client: Client,
    message: Message,
) -> Message:
    """
    Handle start command with file sharing.

    decode_list structure (list):
        [start with channel id, followed with message.id]
    """
    if len(message.command) == 1:
        await message.reply(text=options.settings.START_MESSAGE, quote=True)
        return message.stop_propagation()

    # shouldn't overwrite existing id it already exists
    flt_id = FltId(_id=message.from_user.id).model_dump()
    update = UpdSet(_set=flt_id).model_dump()
    await database.update_one(collection="Users", db_filter=flt_id, update=update, upsert=True)

    try:
        base64_file = message.text.split(maxsplit=1)[1]
        decode_list = Encoding.decode(base64_file)
    except (IndexError, binascii.Error):
        await message.reply(text="Attempted to fetch files: got invalid link")
        return message.stop_propagation()

    try:
        forward_files = await client.forward_messages(
            chat_id=message.chat.id,
            from_chat_id=config.BACKUP_CHANNEL,
            message_ids=decode_list,
            hide_captions=True,
            hide_sender_name=True,
        )
        if not forward_files:
            await message.reply(text="Attempted to fetch files: has be deleted or no longer exist")
            return message.stop_propagation()
    except MessageIdInvalid:
        await message.reply(text="Attempted to fetch files: unknown backup channel source")
        return message.stop_propagation()

    schedule_delete = [msg.id for msg in forward_files] if isinstance(forward_files, list) else [forward_files.id]

    delete_n_seconds = options.settings.AUTO_DELETE_SECONDS
    custom_caption = options.settings.CUSTOM_CAPTION
    forward_caption = await message.reply(text=custom_caption.format(int(delete_n_seconds / 60)))
    schedule_delete.append(forward_caption.id)

    await schedule_manager.schedule_delete(
        client=client,
        chat_id=message.chat.id,
        message_ids=schedule_delete,
        delete_n_seconds=delete_n_seconds,
    )
    return message.stop_propagation()


@Client.on_message(filters.command("start") & filters.private, group=1)
async def return_start(
    client: Client,
    message: Message,
) -> Message | None:
    """
    Handle start command without files or not subscribed.
    """

    buttons = []
    channels_n_invite = client.channels_n_invite  # type: ignore[reportAttributeAccessIssue]
    for channel, invite in channels_n_invite.items():
        buttons.append([InlineKeyboardButton(text=channel, url=invite)])

    return await message.reply(
        text=options.settings.FORCE_SUB_MESSAGE,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        quote=True,
    )
