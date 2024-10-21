import asyncio
import uuid
from typing import Any, ClassVar, TypedDict

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.database import MongoDB
from bot.options import options
from bot.utilities.helpers import DataEncoder, RateLimiter
from bot.utilities.pyrofilters import ConvoMessage, PyroFilters
from bot.utilities.pyrotools import HelpCmd


class CacheEntry(TypedDict):
    """Cache entry for files."""

    counter: int
    files: list[dict]


class MakeFilesCommand:
    """Make files command class."""

    database = MongoDB()
    files_cache: ClassVar[dict[int, CacheEntry]] = {}

    @staticmethod
    @RateLimiter.hybrid_limiter(func_count=1)
    async def message_reply(client: Client, message: Message, **kwargs: Any) -> Message:  # noqa: ANN401, ARG004
        """
        Replies to a message with rate limiter.

        Parameters:
            client (Client): The client instance.
            message (Message): The message to reply to.
            **kwargs (Any): Additional keyword arguments for the reply.

        Returns:
            Message: The replied message.
        """
        return await message.reply(**kwargs)

    @classmethod
    async def handle_convo_start(cls, client: Client, message: ConvoMessage) -> Message:
        """
        Handle conversation start.

        Parameters:
            client (Client): The client instance.
            message (ConvoMessage): The conversation message.

        Returns:
            Message: The replied message.
        """
        unique_id = message.chat.id + message.from_user.id
        cls.files_cache.setdefault(unique_id, {"files": [], "counter": 0})
        return await cls.message_reply(client=client, message=message, text="Send your files.", quote=True)

    @classmethod
    async def handle_conversation(cls, client: Client, message: ConvoMessage) -> Message | None:
        """
        Handle conversations and file uploads. Maintain file cache for optimization.
        Process burst files, responding only when complete.


        Parameters:
            client (Client): The client instance.
            message (ConvoMessage): The conversation message.

        Returns:
            Message or None: The replied message or None if burst is triggered.
        """
        unique_id = message.chat.id + message.from_user.id
        file_type = message.document or message.video or message.photo or message.audio or message.sticker
        if not file_type:
            return await cls.message_reply(
                client=client,
                message=message,
                text="> Only send support files!",
                quote=True,
            )

        cls.files_cache[unique_id]["counter"] += 1
        cls.files_cache[unique_id]["files"].append(
            {
                "caption": message.caption.markdown if message.caption else None,
                "file_id": file_type.file_id,
                "file_name": getattr(file_type, "file_name", file_type.file_unique_id) or file_type.file_unique_id,
                "message_id": message.id,
            },
        )

        current_files_count = cls.files_cache[unique_id]["counter"]
        await asyncio.sleep(0.1)
        if cls.files_cache[unique_id]["counter"] != current_files_count:
            return None

        file_names = "\n".join(i["file_name"] for i in cls.files_cache[unique_id]["files"])
        extra_message = ">File list truncated.\n- Send more files to continue.\n- Use /make_link for a shareable link."
        return await cls.message_reply(
            client=client,
            message=message,
            text=f"```\nFile(s):\n{file_names[-3000:]}\n```\n{extra_message}",
            quote=True,
        )

    @classmethod
    async def handle_convo_stop(cls, client: Client, message: ConvoMessage) -> Message:
        """
        Handle the end of conversation.

        This finalizes the conversation by:
        - Checking if any files were uploaded.
        - Optionally forwarding files to a backup channel.
        - Storing file information in a database.
        - Generating and sending a link to access the files.

        Parameters:
            client (Client): The client instance.
            message (ConvoMessage): The conversation message.

        Returns:
            Message: The replied message.
        """
        forward_limit_size = 100
        unique_id = message.chat.id + message.from_user.id
        user_cache_chunk = [
            [file["message_id"] for file in cls.files_cache[unique_id]["files"][i : i + forward_limit_size]]
            for i in range(0, len(cls.files_cache[unique_id]["files"]), forward_limit_size)
        ]

        if not user_cache_chunk:
            cls.files_cache.pop(unique_id)
            return await cls.message_reply(
                client=client,
                message=message,
                text="No file inputs, stopping task.",
                quote=True,
            )

        files_to_store = []
        if options.settings.BACKUP_FILES:
            for user_cache in user_cache_chunk:
                forwarded_messages = await client.forward_messages(
                    chat_id=config.BACKUP_CHANNEL,
                    from_chat_id=message.chat.id,
                    message_ids=user_cache,
                    hide_sender_name=True,
                )

                for msg in forwarded_messages if isinstance(forwarded_messages, list) else [forwarded_messages]:
                    file_type = msg.document or msg.video or msg.photo or msg.audio or msg.sticker
                    files_to_store.append(
                        {
                            "caption": msg.caption.markdown if msg.caption else None,
                            "file_id": file_type.file_id,
                            "message_id": msg.id,
                        },
                    )
        else:
            # Create a copy of the files cache, excluding the 'file_name' field from each file CacheEntry.
            files_to_store = [
                {k: v for k, v in i.items() if k != "file_name"} for i in cls.files_cache[unique_id]["files"]
            ]

        unique_link = f"{uuid.uuid4().int}"
        file_link = DataEncoder.encode_data(unique_link)
        file_origin = config.BACKUP_CHANNEL if options.settings.BACKUP_FILES else message.chat.id

        add_file = await cls.database.add_file(file_link=file_link, file_origin=file_origin, file_data=files_to_store)

        cls.files_cache.pop(unique_id)

        if add_file:
            link = f"https://t.me/{client.me.username}?start={file_link}"  # type: ignore[reportOptionalMemberAccess]
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Share URL", url=f"https://t.me/share/url?url={link}")]],
            )

            return await cls.message_reply(
                client=client,
                message=message,
                text=f"Here is your link:\n>{link}",
                quote=True,
                reply_markup=reply_markup,
                disable_web_page_preview=True,
            )
        return await message.reply("Couldn't add files to database")


@Client.on_message(
    filters.private
    & PyroFilters.admin(allow_global=True)
    & PyroFilters.create_conversation_filter(
        convo_start=["/make_files", "/batch", "/batch_files"],
        convo_stop=["/make_link", "/batch_link"],
    ),
)
async def make_files_command_handler(client: Client, message: ConvoMessage) -> Message | None:
    """Handles a conversation that receives files to generate an accessable file link.

    **Usage:**
        /make_files: initiate a conversation then send your files.
        /make_link: wraps the conversation and generates a link.
    """
    if message.convo_start:
        return await MakeFilesCommand.handle_convo_start(client=client, message=message)
    if message.conversation:
        return await MakeFilesCommand.handle_conversation(client=client, message=message)
    if message.convo_stop:
        return await MakeFilesCommand.handle_convo_stop(client=client, message=message)
    return None


HelpCmd.set_help(
    command="make_files",
    description=make_files_command_handler.__doc__,
    allow_global=True,
    allow_non_admin=False,
    alias=["/batch", "/batch_files"],
)
