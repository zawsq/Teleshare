from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.database import MongoDB
from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrofilters import ConvoMessage, PyroFilters
from bot.utilities.pyrotools import HelpCmd

database = MongoDB()


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("unban"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def unban_user(client: Client, message: ConvoMessage) -> Message | None:  # noqa: ARG001
    """Unban a user from using the bot

    **Usage:**
        /unban [user id]
    """
    user_id = None

    if len(message.command) >= 2:  # noqa: PLR2004
        user_id = int(message.command[1]) if message.command[1].isdigit() else None

    if user_id:
        ban_user = await database.unban_user(user_id)

        if ban_user:
            return await message.reply(text=f"User: `{user_id}` has been unbanned", quote=True)
        return await message.reply(text=f"Cannot find: `{user_id}`", quote=True)
    return await message.reply(text=f"Please input a valid user id: `{user_id}`", quote=True)


HelpCmd.set_help(
    command="unban",
    description=unban_user.__doc__,
    allow_global=False,
    allow_non_admin=False,
)
