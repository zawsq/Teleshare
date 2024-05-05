from pyrogram import filters
from pyrogram.client import Client
from pyrogram.errors import InputUserDeactivated, UserIsBlocked
from pyrogram.types import Message

from bot.database import MongoDB
from bot.utilities.pyrofilters import PyroFilters

database = MongoDB("Zaws-File-Share")


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("broadcast"),
)
async def broadcast(client: Client, message: Message) -> Message:  # noqa: ARG001
    if not message.reply_to_message:
        return await message.reply(text="Reply to a message with command /broadcast to avoid broadcasting typos.")

    successful = 0
    unsuccessful_ids = []

    pipeline_ids = [
        {"$project": {"_id": 1}},
        {"$group": {"_id": None, "user_ids": {"$addToSet": "$_id"}}},
        {"$project": {"_id": 0, "user_ids": 1}},
    ]

    user_ids = (await database.aggregate(collection="Users", pipeline=pipeline_ids))[0]["user_ids"]

    notice_message = await message.reply(text="Currently broadcasting... This may take a while.", quote=True)

    for user_id in user_ids:
        try:
            await message.reply_to_message.copy(user_id)
            successful += 1
        except (UserIsBlocked, InputUserDeactivated):  # noqa: PERF203
            unsuccessful_ids.append(user_id)

    if unsuccessful_ids:
        await database.delete_many(
            collection="Users",
            db_filter={"_id": {"$in": unsuccessful_ids}},
        )

    return await notice_message.edit(
        text=f">Broadcasting Finished:\nSuccessful: {successful}\nUnsuccessful: {len(unsuccessful_ids)}",
    )
