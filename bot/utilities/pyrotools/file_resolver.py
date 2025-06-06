import contextlib
from itertools import groupby
from typing import TYPE_CHECKING, Any, cast

from pydantic import BaseModel
from pyrogram.client import Client
from pyrogram.file_id import FileId
from pyrogram.types import InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo, Message

from bot.options import options

if TYPE_CHECKING:
    from collections.abc import Callable


class FileResolverModel(BaseModel):
    """
    Represents a file resolver.

    Parameters:
        file_id (str): The file ID.
        caption (str | None): The file caption.
    """

    caption: str | None
    file_id: str
    message_id: int
    media_group_id: int | None = None


class UnsupportedFileError(Exception):
    """
    Raised when an unsupported file type is encountered.
    """

    def __init__(self, file_type: FileId | None) -> None:
        super().__init__(f"Unsupported file: {file_type}")


class SendMedia:
    """
    Provides methods for sending media files.
    """

    @classmethod
    async def send_media(
        cls,
        client: Client,
        chat_id: int,
        file_data: FileResolverModel,
        file_origin: int,
        protect_content: bool,  # noqa: FBT001
    ) -> Message:
        """
        Sends a media file.

        Parameters:
            client (Client): The Pyrogram client.
            chat_id (int): The chat ID.
            file_data (FileResolverModel): The file data.
            file_origin: (int | None): Where the file came from.

        Returns:
            Message: The sent message.

        Raises:
            UnsupportedFileError: If the file type is unsupported.
        """

        if options.settings.BACKUP_FILES:
            get_file = await client.get_messages(chat_id=file_origin, message_ids=file_data.message_id)
            if not getattr(get_file, "empty", False):
                return cast("Message", await get_file.copy(chat_id=chat_id))  # pyright: ignore[reportCallIssue]

        file_type_data = FileId.decode(file_id=file_data.file_id)
        methods: dict[str, Callable[..., Any]] = {
            "AUDIO": client.send_audio,
            "DOCUMENT": client.send_document,
            "PHOTO": client.send_photo,
            "VIDEO": client.send_video,
            "STICKER": client.send_sticker,
        }
        if file_type_data:
            file_type = file_type_data.file_type.name
            if file_type in methods:
                file_kwargs: dict[str, int | str] = {
                    "chat_id": chat_id,
                    file_type.lower(): file_data.file_id,
                    "protect_content": protect_content,
                }

                if file_type != "STICKER":
                    file_kwargs["caption"] = file_data.caption or ""

                return await methods[file_type](
                    **file_kwargs,  # pyright: ignore[reportCallIssue]
                    # https://github.com/microsoft/pyright/issues/5069#issuecomment-1533839392
                )

        raise UnsupportedFileError(file_type_data)

    @classmethod
    async def send_media_group(
        cls,
        client: Client,
        chat_id: int,
        file_data: list[FileResolverModel],
        protect_content: bool,  # noqa: FBT001
    ) -> list[Message]:
        input_media: dict[str, Callable[..., Any]] = {
            "AUDIO": InputMediaAudio,
            "DOCUMENT": InputMediaDocument,
            "PHOTO": InputMediaPhoto,
            "VIDEO": InputMediaVideo,
        }

        media_group = []
        for i in file_data:
            file_type_data = FileId.decode(file_id=i.file_id)
            if not file_type_data:
                continue

            file_type = file_type_data.file_type.name
            if file_type in input_media:
                media_group.append(input_media[file_type](media=i.file_id, caption=i.caption or ""))

        return await client.send_media_group(chat_id=chat_id, media=media_group, protect_content=protect_content)

    @classmethod
    async def send_media_manager(
        cls,
        client: Client,
        chat_id: int,
        file_data: list[FileResolverModel],
        file_origin: int,
        protect_content: bool,  # noqa: FBT001
    ) -> Message | list[Message]:
        """
        Sends a media group.

        Parameters:
            client (Client): The Pyrogram client.
            chat_id (int): The chat ID.
            file_data (list[FileResolverModel]): The list of file data.
            file_origin: int: Where the file came from.

        Returns:
            Message: The sent message.
        """
        messaage_ids = [i.message_id for i in file_data]
        send_files = await client.forward_messages(
            chat_id=chat_id,
            from_chat_id=file_origin,
            message_ids=messaage_ids,
            protect_content=protect_content,
            hide_sender_name=True,
        )

        if send_files:
            return send_files

        re_group_file_datas = [
            list(g) if k[0] else next(g)
            for k, g in groupby(
                file_data,
                key=lambda x: (
                    x.media_group_id is not None,
                    x.media_group_id if x.media_group_id is not None else id(x),
                ),
            )
        ]

        send_files_message = []
        for i in re_group_file_datas:
            if isinstance(i, list):
                send_files_message.extend(
                    await cls.send_media_group(
                        client=client,
                        chat_id=chat_id,
                        file_data=i,
                        protect_content=protect_content,
                    ),
                )
            else:
                with contextlib.suppress(UnsupportedFileError):
                    send_files_message.append(
                        await cls.send_media(
                            client=client,
                            chat_id=chat_id,
                            file_data=i,
                            file_origin=file_origin,
                            protect_content=protect_content,
                        ),
                    )

        return send_files_message
