from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.config import config
from bot.options import InvalidValueError, options

DEFAULT_ARGUMENT = 1
MISSING_ARGUMENT = 2
TO_UPDATE = """Usage: /option key new_value
ex: /option AUTO_DELETE_SECONDS 600

this sets `AUTO_DELETE_SECONDS` as 600 seconds or 10 minutes"""


@Client.on_message(filters.private & filters.command("option"))
async def option_config(client: Client, message: Message) -> Message | None:  # noqa: ARG001
    if message.from_user.id not in config.ROOT_ADMINS_ID:
        return None

    cmd = message.command

    if len(cmd) == DEFAULT_ARGUMENT:
        return await message.reply(
            text=f"```\n{options.settings.model_dump_json(indent=2)}```\n{TO_UPDATE}",
            quote=True,
        )

    if len(cmd) == MISSING_ARGUMENT:
        return await message.reply(text=f"missing arguments:\n{TO_UPDATE}", quote=True)

    key = cmd[1]
    change_value = int(cmd[2]) if cmd[2].isdigit() else cmd[2]

    try:
        update = await options.update_settings(key=key, value=change_value)

        final_message = await message.reply(text=f"Updated:```\n{update.model_dump_json(indent=2)}```", quote=True)
    except (InvalidValueError, KeyError):
        final_message = await message.reply(
            text="Please provide an existing key with int or digit for int value and str for str values",
            quote=True,
        )

    return final_message
