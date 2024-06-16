import asyncio

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.errors import FloodWait, InputUserDeactivated, PeerIdInvalid, UserIsBlocked
from pyrogram.types import Message

from bot.config import config
from bot.database import MongoDB
from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrofilters import PyroFilters
from bot.utilities.pyrotools import HelpCmd

database = MongoDB(database=config.MONGO_DB_NAME)


@RateLimiter.hybrid_limiter(func_count=1)
async def message_copy_wrapper(client: Client, message: Message, chat_id: int) -> None:  # noqa: ARG001
    try:
        await message.reply_to_message.copy(chat_id)
    except FloodWait as e:
        await asyncio.sleep(e.value)  # pyright: ignore[reportArgumentType]
        await message.reply_to_message.copy(chat_id)


async def broadcast_sender(
    client: Client,
    message: Message,
    user_ids: list,
    user_ids_codex: list,
) -> dict:
    """
    Copies a message to broadcast on multiple users.

    Parameters:
        message (Message): The message to be copied.
        user_ids (list): A list of user IDs to copy the message to.
        user_ids_codex (list): A list of user IDs to copy the message to (codex).

    Returns:
        dict: A dictionary containing the number of successful and unsuccessful message copies.
    """
    successful = 0
    unsuccessful_ids = []
    unsuccessful_ids_codex = []

    for user_id in list(set(user_ids + user_ids_codex)):
        try:
            message.chat.id = user_id
            await message_copy_wrapper(client=client, message=message, chat_id=user_id)
            successful += 1
        except (UserIsBlocked, InputUserDeactivated, PeerIdInvalid):  # noqa: PERF203
            unsuccessful_ids.append(user_id) if user_id in user_ids else unsuccessful_ids_codex.append(user_id)

    if unsuccessful_ids:
        await database.delete_many(
            collection="Users",
            db_filter={"_id": {"$in": unsuccessful_ids}},
        )
    if unsuccessful_ids_codex:
        await database.delete_many(
            collection="users",
            db_filter={"_id": {"$in": unsuccessful_ids_codex}},
        )

    return {"successful": successful, "unsuccessful": len(unsuccessful_ids + unsuccessful_ids_codex)}


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("broadcast"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def broadcast(client: Client, message: Message) -> Message:
    """Broadcasts a message to multiple subscribed users
    this command may take awhile depending on user count.

    **Usage:**
        create a message then reply with /broadcast to avoid typos.
    """
    if not message.reply_to_message:
        return await message.reply(text="Reply to a message with command /broadcast to avoid broadcasting typos.")

    pipeline_ids = [
        {"$project": {"_id": 1}},
        {"$group": {"_id": None, "user_ids": {"$addToSet": "$_id"}}},
        {"$project": {"_id": 0, "user_ids": 1}},
    ]

    user_ids = (await database.aggregate(collection="Users", pipeline=pipeline_ids))[0]["user_ids"]
    user_ids_codex = await database.aggregate(collection="users", pipeline=pipeline_ids)

    if user_ids_codex:
        user_ids_codex = user_ids_codex[0]["user_ids"]

    notice_message = await message.reply(text="Currently broadcasting... This may take a while.", quote=True)

    result = await broadcast_sender(
        client=client,
        message=message,
        user_ids=user_ids,
        user_ids_codex=user_ids_codex,
    )

    successful = result["successful"]
    unsuccessful = result["unsuccessful"]

    return await notice_message.edit(
        text=f">Broadcasting Finished:\nSuccessful: {successful}\nUnsuccessful: {unsuccessful}",
    )


HelpCmd.set_help(
    command="broadcast",
    description=broadcast.__doc__,
    allow_global=False,
    allow_non_admin=False,
)
