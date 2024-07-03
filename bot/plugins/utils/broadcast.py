import asyncio
from typing import cast

from pydantic import BaseModel
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


class BroadcastConfig(BaseModel):
    user_ids: list[int]
    user_ids_codex: list[int]
    pin: bool


class BroadcastHandler:
    """A handler class for broadcasting messages to multiple users."""

    @staticmethod
    @RateLimiter.hybrid_limiter(func_count=1)
    async def message_copy_wrapper(
        client: Client,  # noqa: ARG004
        message: Message,
        chat_id: int,
        pin: bool,  # noqa: FBT001
    ) -> Message | list[Message]:
        """
        Copy a message to a specified chat ID, handling rate limits and optional pinning.

        Parameters:
            client (Client): The Pyrogram client instance.
            message (Message): The message object to be copied.
            chat_id (int): The ID of the chat to copy the message to.
            pin (bool): Whether to pin the copied message.

        Returns:
            Message | list[Message]: The copied message(s).
        """

        async def copy_and_pin() -> Message | list[Message]:
            broadcast_message = await message.reply_to_message.copy(chat_id)
            if pin:
                if isinstance(broadcast_message, list):
                    for msg in broadcast_message:
                        await msg.pin(both_sides=True)
                else:
                    await broadcast_message.pin(both_sides=True)
            return broadcast_message

        try:
            return await copy_and_pin()
        except FloodWait as e:
            await asyncio.sleep(float(cast(float, e.value)))
            return await copy_and_pin()

    @staticmethod
    async def cleanup_users(unsuccessful_ids: list, unsuccessful_ids_codex: list) -> None:
        """Cleans up users from database based on their IDs.

        Parameters:
            unsuccessful_ids (list): List of user unsuccessful id from teleshare to be delete from the database.
            unsuccessful_ids_codex (list): List of user unsuccessful id from CodeXbotz to be delete from the database.
        """
        if unsuccessful_ids:
            await database.delete_many(collection="Users", db_filter={"_id": {"$in": unsuccessful_ids}})

        if unsuccessful_ids_codex:
            await database.delete_many(collection="users", db_filter={"_id": {"$in": unsuccessful_ids_codex}})

    @classmethod
    async def broadcast_sender(cls, client: Client, message: Message, broadcast_config: BroadcastConfig) -> dict:
        """
        Sends a message to multiple users and handles success and failure counts.

        Parameters:
            client (Client): The Pyrogram client instance.
            message (Message): The message object to be broadcasted.
            user_ids (list): List of user IDs to send the message to from teleshare.
            user_ids_codex (list): List of user IDs to send the message to from CodeXbotz.

        Returns:
            dict: Dictionary containing successful and unsuccessful message counts.
        """
        successful, unsuccessful_ids, unsuccessful_ids_codex = 0, [], []
        for user_id in list(set(broadcast_config.user_ids + broadcast_config.user_ids_codex)):
            try:
                # Required so rate limiter from message_copy_wrapper() can properly handle it.
                message.chat.id = user_id
                await cls.message_copy_wrapper(
                    client=client,
                    message=message,
                    chat_id=user_id,
                    pin=broadcast_config.pin,
                )
                successful += 1
            except (UserIsBlocked, InputUserDeactivated, PeerIdInvalid):  # noqa: PERF203
                unsuccessful_ids.append(
                    user_id,
                ) if user_id in broadcast_config.user_ids else unsuccessful_ids_codex.append(user_id)

        await cls.cleanup_users(unsuccessful_ids=unsuccessful_ids, unsuccessful_ids_codex=unsuccessful_ids_codex)
        return {"successful": successful, "unsuccessful": len(unsuccessful_ids + unsuccessful_ids_codex)}


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("broadcast"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def broadcast(client: Client, message: Message) -> Message:
    """Broadcasts a message to multiple subscribed users
    this command may take awhile depending on user count.

    **Usage:**
        Create a message then reply with /broadcast to avoid typos.
        To pin the broadcast message add additional arg to the command:
        `/broadcast pin`
    """
    if not message.reply_to_message:
        return await message.reply(text="Reply to a message with command /broadcast to avoid broadcasting typos.")

    pin_arg = bool((message.command[1]).lower() == "pin") if message.command[1:] else False

    pipeline_ids = [
        {"$project": {"_id": 1}},
        {"$group": {"_id": None, "user_ids": {"$addToSet": "$_id"}}},
        {"$project": {"_id": 0, "user_ids": 1}},
    ]

    user_ids = (await database.aggregate(collection="Users", pipeline=pipeline_ids))[0]["user_ids"]
    user_ids_codex = await database.aggregate(collection="users", pipeline=pipeline_ids)

    user_ids_codex = user_ids_codex[0]["user_ids"] if user_ids_codex else []

    notice_message = await message.reply(text="Currently broadcasting... This may take a while.", quote=True)

    result = await BroadcastHandler.broadcast_sender(
        client=client,
        message=message,
        broadcast_config=BroadcastConfig(user_ids=user_ids, user_ids_codex=user_ids_codex, pin=pin_arg),
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
