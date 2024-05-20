from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.database import MongoDB
from bot.options import options
from bot.utilities.helpers import DataEncoder, DataValidationError
from bot.utilities.pyrofilters import PyroFilters
from bot.utilities.pyrotools import FileResolverModel, Pyrotools
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
    """
    if not message.command[1:]:
        await message.reply(text=options.settings.START_MESSAGE, quote=True)
        return message.stop_propagation()

    # shouldn't overwrite existing id it already exists
    await database.update_one(
        collection="Users",
        db_filter={"_id": message.from_user.id},
        update={"$set": {"_id": message.from_user.id}},
        upsert=True,
    )

    base64_file_link = message.text.split(maxsplit=1)[1]
    file_document = await database.aggregate(collection="Files", pipeline=[{"$match": {"_id": base64_file_link}}])

    if not file_document:
        try:
            codex_message_ids = DataEncoder.codex_decode(
                base64_string=base64_file_link,
                backup_channel=config.BACKUP_CHANNEL,
            )
        except DataValidationError:
            await message.reply(text="Attempted to resolve link: Got invalid link.")
            return message.stop_propagation()

        if len(codex_message_ids) == 1:
            send_files = await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=config.BACKUP_CHANNEL,
                message_id=codex_message_ids[0],
            )

        else:
            send_files = await client.forward_messages(
                chat_id=message.chat.id,
                from_chat_id=config.BACKUP_CHANNEL,
                message_ids=codex_message_ids,
                hide_sender_name=True,
            )
        if not send_files:
            await message.reply(text="Attempted to fetch files: Does not exist.")
            return message.stop_propagation()
    else:
        file_document = file_document[0]
        files = [FileResolverModel(**file) for file in file_document["files"]]

        if len(files) == 1:
            send_files = await Pyrotools.send_media(client=client, chat_id=message.chat.id, file_data=files[0])
        else:
            file_origin = file_document["file_origin"]
            send_files = await Pyrotools.send_media_group(
                client=client,
                chat_id=message.chat.id,
                file_data=files,
                file_origin=file_origin,
            )

    delete_n_seconds = options.settings.AUTO_DELETE_SECONDS

    if delete_n_seconds != 0:
        schedule_delete_message = [msg.id for msg in send_files] if isinstance(send_files, list) else [send_files.id]

        custom_caption = options.settings.CUSTOM_CAPTION
        forward_caption = await message.reply(text=custom_caption.format(int(delete_n_seconds / 60)))
        schedule_delete_message.append(forward_caption.id)

        await schedule_manager.schedule_delete(
            client=client,
            chat_id=message.chat.id,
            message_ids=schedule_delete_message,
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

    channels_n_invite = client.channels_n_invite  # type: ignore[reportAttributeAccessIssue]
    buttons = []

    for channel, invite in channels_n_invite.items():
        buttons.append([InlineKeyboardButton(text=channel, url=invite)])

    if message.command[1:]:
        link = f"https://t.me/{client.me.username}?start={message.command[1]}"  # type: ignore[reportOptionalMemberAccess]
        buttons.append([InlineKeyboardButton(text="Try Again", url=link)])

    return await message.reply(
        text=options.settings.FORCE_SUB_MESSAGE,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        quote=True,
    )
