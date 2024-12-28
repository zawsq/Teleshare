from inspect import cleandoc

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.config import config
from bot.options import InvalidValueError, options
from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrofilters import PyroFilters
from bot.utilities.pyrotools import HelpCmd

MISSING_ARGUMENT = 2
BOOLEN_CONVERT = {"true": True, "false": False}


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command(["option", "settings"]),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def option_config_cmd(client: Client, message: Message) -> Message | None:  # noqa: ARG001
    """Use to configure database options.

    **Usage:**
        /option key new_value
        /option key [reply to a message]

    **Example:**
        /option AUTO_DELETE_SECONDS 600
        /option FORCE_SUB_MESSAGE: reply to a message.
    """

    cmd = message.command

    if not cmd[1:]:
        options_configs = options.settings.model_dump()
        format_options = "\n".join(f"**{key}** ```\n{value}```" for key, value in options_configs.items())
        func_doc = option_config_cmd.__doc__
        return await message.reply(
            text=f"{format_options}\n\n{cleandoc(func_doc) if func_doc else ''}",
            quote=True,
        )

    key = cmd[1].upper()

    if len(cmd) == MISSING_ARGUMENT and not message.reply_to_message:
        return await message.reply(text=f"missing arguments:\n{option_config_cmd.__doc__}", quote=True)

    if key not in options.settings.__fields__:
        return await message.reply("Please use a valid key to edit")

    if message.reply_to_message:
        values = message.reply_to_message.text.markdown if message.reply_to_message.text is not None else None
        if not values or not values.isdigit():
            copyied_mssg = await message.reply_to_message.copy(chat_id=config.BACKUP_CHANNEL)
            values = str(copyied_mssg.id if isinstance(copyied_mssg, Message) else values)
    else:
        # messages next to option command.
        values = (message.text.markdown.split(maxsplit=2)[2:])[0].lstrip()

    try:
        change_value = int(values) if values.isdigit() else BOOLEN_CONVERT.get(values.lower(), values)

        update = await options.update_settings(key=key, value=change_value)
        options_configs = update.model_dump()
        format_options = "\n".join(f"**{key}** ```\n{value}```" for key, value in options_configs.items())

        final_message = await message.reply(
            text=f"Updated:\n{format_options}\n\n__Note: if you see number instead of text it means it set a message to copy (this happens if you use reply to a message while setting the option key)__",  # noqa: E501
            quote=True,
        )
    except InvalidValueError:
        final_message = await message.reply(
            text="Please provide an existing key with int or digit for int value and str for str values",
            quote=True,
        )

    return final_message


HelpCmd.set_help(
    command="option",
    description=option_config_cmd.__doc__,
    allow_global=False,
    allow_non_admin=False,
    alias=["settings"],
)
