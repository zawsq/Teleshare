from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.database import MongoDB
from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrofilters import PyroFilters

database = MongoDB()


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("stats"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def help_command(client: Client, message: Message) -> Message:  # noqa: ARG001
    """A command to display links and users count.:

    **Usage:**
        /stats
    """

    link_count, users_count = await database.stats()

    return await message.reply(f">STATS:\n**Users Count:** `{users_count}`\n**Links Count:** `{link_count}`")
