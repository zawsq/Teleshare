from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.database import MongoDB
from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrofilters import ConvoMessage, PyroFilters
from bot.utilities.pyrotools import HelpCmd

database = MongoDB()


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("ban"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def ban_user(client: Client, message: ConvoMessage) -> Message | None:  # noqa: ARG001
    """Ban a user from using the bot

    **Usage:**
        /ban [user id]
    """
    user_id = None

    if len(message.command) >= 2:  # noqa: PLR2004
        user_id = int(message.command[1]) if message.command[1].isdigit() else None

    if user_id:
        ban_user = await database.ban_user(user_id)

        if ban_user:
            return await message.reply(text=f"User: `{user_id}` has been banned", quote=True)
        return await message.reply(f"Cannot find: `{user_id}`", quote=True)
    return await message.reply(text=f"Please input a valid user id: `{user_id}`", quote=True)


HelpCmd.set_help(
    command="ban",
    description=ban_user.__doc__,
    allow_global=False,
    allow_non_admin=False,
)
