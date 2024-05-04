from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.utilities.helpers import Encoding
from bot.utilities.pyrofilters import ConvoMessage, PyroFilters

files_cache = {}


@Client.on_message(
    filters.private
    & PyroFilters.create_conversation_filter(
        convo_start="/make_files",
        convo_stop="/make_link",
    ),
)
async def make_files_command(client: Client, message: ConvoMessage) -> Message | None:
    """
    Handle the conversation start, conversation, and stop states.

    Example:
        User sends /make_files to start the conversation, then sends multiple documents,
        and finally sends /make_link to stop the conversation and receive a sharable link.

    """
    unique_id = message.chat.id + message.from_user.id
    if message.convo_start:
        files_cache.setdefault(unique_id, {})
        return await message.reply("Send your files.")

    if message.conversation:
        if not message.document:
            return await message.reply("Please only send documents.")

        files_cache[unique_id].update({message.id: message.document.file_name})

        file_names = "\n".join(files_cache[unique_id].values())
        extra_message = "- Send more documents for batch files.\n- Send /make_link to create a sharable link."
        return await message.reply(text=f"```\nFile(s):\n{file_names}\n```\n{extra_message}")

    if message.convo_stop:
        file_ids = list(files_cache[unique_id].keys())
        if not file_ids:
            return await message.reply("No file inputs, stopping task.")

        create_backup_reply = await message.reply("Processing, please wait...")
        forwarded_messages = await client.forward_messages(
            chat_id=config.BACKUP_CHANNEL,
            from_chat_id=message.chat.id,
            message_ids=file_ids,
            hide_captions=True,
            hide_sender_name=True,
        )

        if isinstance(forwarded_messages, list):
            file_ids_backup = [msg.id for msg in forwarded_messages]
        else:
            file_ids_backup = [forwarded_messages.id]

        encoded_file_ids = Encoding.encode(file_ids_backup)
        files_cache.pop(unique_id)
        await create_backup_reply.delete()

        link = f"https://t.me/{client.me.username}?start={encoded_file_ids}"  # type: ignore[reportOptionalMemberAccess]
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Share URL", url=f"https://t.me/share/url?url={link}")]],
        )

        return await message.reply(
            text=f"Here is your link:\n>{link}",
            quote=True,
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )

    return None
