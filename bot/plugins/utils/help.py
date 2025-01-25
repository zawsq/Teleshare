from inspect import cleandoc

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.config import config
from bot.options import options
from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrotools import HelpCmd


@Client.on_message(
    filters.private & filters.command("help"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def help_command(client: Client, message: Message) -> Message:  # noqa: ARG001
    """A command to display all available help commands:

    **Usage:**
        /help [command]
    """
    is_root_admin = message.from_user.id in config.ROOT_ADMINS_ID
    global_mode = options.settings.GLOBAL_MODE

    if not message.command[1:]:
        available_commands = sorted(
            HelpCmd.get_cmds()
            if is_root_admin
            else HelpCmd.get_global_cmds()
            if global_mode
            else HelpCmd.get_non_admin_cmds(),
        )

        format_cmds = "\n".join(available_commands)
        instructions = f"List of all available commands:```\n{format_cmds}```\n\n{cleandoc(help_command.__doc__) if help_command.__doc__ else ''}"  # noqa: E501

        return await message.reply(text=instructions, quote=True)

    command_info = HelpCmd.get_help(command=message.command[1])

    if not command_info:
        return await message.reply(text="This command does not exists.", quote=True)

    instructions = cleandoc(f"""**Command**: {message.command[1]}
    **Alias**: {command_info.get("alias")}

    **Description**:
        {command_info.get("description")}""")

    return await message.reply(text=instructions, quote=True)
