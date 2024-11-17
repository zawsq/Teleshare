from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.database import MongoDB
from bot.options import options
from bot.utilities.helpers import DataEncoder, DataValidationError, PyroHelper, RateLimiter
from bot.utilities.pyrofilters import PyroFilters
from bot.utilities.pyrotools import FileResolverModel, HelpCmd, Pyrotools
from bot.utilities.schedule_manager import schedule_manager

database = MongoDB()


class FileSender:
    """Used to manage file sending functions between codexbotz and teleshare."""

    forward_limit_size = 100

    @staticmethod
    async def codexbotz(
        client: Client,
        codex_message_ids: list[int],
        chat_id: int,
        from_chat_id: int,
        protect_content: bool,  # noqa: FBT001
    ) -> list[Message]:
        all_sent_files = []

        if len(codex_message_ids) == 1:
            send_files = await client.copy_message(
                chat_id=chat_id,
                from_chat_id=from_chat_id,
                message_id=codex_message_ids[0],
                protect_content=protect_content,
            )

            all_sent_files.append(send_files)

        else:
            codex_message_ids_chunk = [
                codex_message_ids[i : i + FileSender.forward_limit_size]
                for i in range(0, len(codex_message_ids), FileSender.forward_limit_size)
            ]

            for codex_files in codex_message_ids_chunk:
                send_files = await client.forward_messages(
                    chat_id=chat_id,
                    from_chat_id=from_chat_id,
                    message_ids=codex_files,
                    hide_sender_name=True,
                    protect_content=protect_content,
                )
                all_sent_files.extend(send_files) if isinstance(send_files, list) else all_sent_files.append(send_files)

        return all_sent_files

    @staticmethod
    async def teleshare(
        client: Client,
        chat_id: int,
        file_data: list[FileResolverModel],
        file_origin: int,
        protect_content: bool,  # noqa: FBT001
    ) -> list[Message]:
        all_sent_files = []

        if len(file_data) == 1:
            send_files = await Pyrotools.send_media(
                client=client,
                chat_id=chat_id,
                file_data=file_data[0],
                file_origin=file_origin,
                protect_content=protect_content,
            )
            all_sent_files.append(send_files)
        else:
            file_data_chunk = [
                file_data[i : i + FileSender.forward_limit_size]
                for i in range(0, len(file_data), FileSender.forward_limit_size)
            ]

            for i_file_data in file_data_chunk:
                send_files = await Pyrotools.send_media_group(
                    client=client,
                    chat_id=chat_id,
                    file_data=i_file_data,
                    file_origin=file_origin,
                    protect_content=protect_content,
                )
                all_sent_files.extend(send_files) if isinstance(send_files, list) else all_sent_files.append(send_files)
        return all_sent_files


@Client.on_message(
    filters.command("start") & filters.private & PyroFilters.subscription(),
    group=0,
)
@RateLimiter.hybrid_limiter(func_count=1)
async def file_start(
    client: Client,
    message: Message,
) -> Message:
    """
    Handle start command, it returns files if a link is included otherwise sends the user a request.

    **Usage:**
        /start [optional file_link]
    """
    if not message.command[1:]:
        await PyroHelper.option_message(client=client, message=message, option_key=options.settings.START_MESSAGE)
        return message.stop_propagation()

    # shouldn't overwrite existing id it already exists
    await database.add_user(user_id=message.from_user.id)

    base64_file_link = message.text.split(maxsplit=1)[1]
    file_document = await database.get_link_document(base64_file_link=base64_file_link)

    if not file_document:
        try:
            codex_message_ids = DataEncoder.codex_decode(
                base64_string=base64_file_link,
                backup_channel=config.BACKUP_CHANNEL,
            )
        except (DataValidationError, IndexError):
            await message.reply(text="Attempted to resolve link: Got invalid link.")
            return message.stop_propagation()

        send_files = await FileSender.codexbotz(
            client=client,
            codex_message_ids=codex_message_ids,
            chat_id=message.chat.id,
            from_chat_id=config.BACKUP_CHANNEL,
            protect_content=config.PROTECT_CONTENT,
        )
        if not send_files:
            await message.reply(text="Attempted to fetch files: Does not exist.")
            return message.stop_propagation()
    else:
        file_origin = file_document["file_origin"]
        file_data = [FileResolverModel(**file) for file in file_document["files"]]

        send_files = await FileSender.teleshare(
            client=client,
            chat_id=message.chat.id,
            file_data=file_data,
            file_origin=file_origin,
            protect_content=config.PROTECT_CONTENT,
        )

    delete_n_seconds = options.settings.AUTO_DELETE_SECONDS

    if delete_n_seconds != 0:
        schedule_delete_message = [msg.id for msg in send_files]

        auto_delete_message = (
            options.settings.AUTO_DELETE_MESSAGE.format(int(delete_n_seconds / 60))
            if not isinstance(options.settings.AUTO_DELETE_MESSAGE, int)
            else options.settings.AUTO_DELETE_MESSAGE
        )
        auto_delete_message_reply = await PyroHelper.option_message(
            client=client,
            message=message,
            option_key=auto_delete_message,
        )
        schedule_delete_message.append(auto_delete_message_reply.id)

        await schedule_manager.schedule_delete(
            client=client,
            chat_id=message.chat.id,
            message_ids=schedule_delete_message,
            delete_n_seconds=delete_n_seconds,
        )
    return message.stop_propagation()


@Client.on_message(filters.command("start") & filters.private, group=1)
@RateLimiter.hybrid_limiter(func_count=1)
async def return_start(
    client: Client,
    message: Message,
) -> Message | None:
    """
    Handle start command without files or not subscribed.
    """

    channels_n_invite = client.channels_n_invite  # type: ignore[reportAttributeAccessIssue]
    buttons = []

    for channel, invite in channels_n_invite.items():
        buttons.append([InlineKeyboardButton(text=channel, url=invite)])

    if message.command[1:]:
        link = f"https://t.me/{client.me.username}?start={message.command[1]}"  # type: ignore[reportOptionalMemberAccess]
        buttons.append([InlineKeyboardButton(text="Try Again", url=link)])

    return await PyroHelper.option_message(
        client=client,
        message=message,
        option_key=options.settings.FORCE_SUB_MESSAGE,
        reply_markup=InlineKeyboardMarkup(buttons),
    )


HelpCmd.set_help(
    command="start",
    description=file_start.__doc__,
    allow_global=True,
    allow_non_admin=True,
)
