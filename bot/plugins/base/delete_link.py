from inspect import cleandoc

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.config import config
from bot.database import MongoDB
from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrofilters import PyroFilters
from bot.utilities.pyrotools import FileResolverModel, HelpCmd

database = MongoDB()


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("delete_link"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def delete_link(client: Client, message: Message) -> Message:
    """Delete an existing link.

    **Usage:**
        /delete_link [link]
    """
    if not message.command[1:]:
        return await message.reply(text=cleandoc(delete_link.__doc__ or ""), quote=True)

    base64_file_link = message.text.split("start=")[1]
    file_document = await database.get_link_document(base64_file_link=base64_file_link)

    if not file_document:
        return await message.reply(
            text="Cannot find link: Either it has been deleted or it does not exist.",
            quote=True,
        )

    file_origin = file_document["file_origin"]
    file_data = [FileResolverModel(**file) for file in file_document["files"]]

    delete_link_document = await database.delete_link_document(base64_file_link=base64_file_link)

    if file_origin == config.BACKUP_CHANNEL and delete_link_document:
        message_ids = [i.message_id for i in file_data]
        await client.delete_messages(chat_id=file_origin, message_ids=message_ids)

    return await message.reply(text=f">**Successfully Deleted:**\n `{base64_file_link}`", quote=True)


HelpCmd.set_help(
    command="delete_link",
    description=delete_link.__doc__,
    allow_global=False,
    allow_non_admin=False,
)
