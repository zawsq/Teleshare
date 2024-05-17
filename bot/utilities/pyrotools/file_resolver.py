from typing import TYPE_CHECKING, Any

from pydantic import BaseModel
from pyrogram.client import Client
from pyrogram.errors import MediaInvalid
from pyrogram.file_id import FileId
from pyrogram.types import InputMediaAudio, InputMediaDocument, InputMediaPhoto, InputMediaVideo, Message

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
    async def send_media(cls, client: Client, chat_id: int, file_data: FileResolverModel) -> Message:
        """
        Sends a media file.

        Parameters:
            client (Client): The Pyrogram client.
            chat_id (int): The chat ID.
            file_data (FileResolverModel): The file data.

        Returns:
            Message: The sent message.

        Raises:
            UnsupportedFileError: If the file type is unsupported.
        """
        file_type_data = FileId.decode(file_id=file_data.file_id)
        methods: dict[str, Callable[[str, str, str], Any]] = {
            "AUDIO": client.send_audio,
            "DOCUMENT": client.send_document,
            "PHOTO": client.send_photo,
            "VIDEO": client.send_video,
        }
        if file_type_data:
            file_type = file_type_data.file_type.name
            if file_type in methods:
                file_kwargs: dict[str, int | str] = {
                    "chat_id": chat_id,
                    file_type.lower(): file_data.file_id,
                    "caption": file_data.caption or "",
                }
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
        file_origin: int,
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
        methods = {
            "AUDIO": InputMediaAudio,
            "DOCUMENT": InputMediaDocument,
            "PHOTO": InputMediaPhoto,
            "VIDEO": InputMediaVideo,
        }
        files = []
        for i in file_data:
            file_id_decoded = FileId.decode(file_id=i.file_id)
            if file_id_decoded is not None:
                file_type = file_id_decoded.file_type.name
                if file_type in methods:
                    files.append(methods[file_type](media=i.file_id, caption=i.caption or ""))
        try:
            return await client.send_media_group(chat_id=chat_id, media=files)
        except MediaInvalid:
            messaage_ids = [i.message_id for i in file_data]
            return await client.forward_messages(
                chat_id=chat_id,
                from_chat_id=file_origin,
                message_ids=messaage_ids,
                hide_sender_name=True,
            )
