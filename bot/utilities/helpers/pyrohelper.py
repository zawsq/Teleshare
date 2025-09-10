from typing import Any, TypedDict, cast

from pyrogram import raw
from pyrogram.client import Client
from pyrogram.errors import UserIsBlocked
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import ChannelInfo, config


class NoInviteLinkError(Exception):
    def __init__(self, channel: int | str) -> None:
        super().__init__(f"{channel} has no invite link")


class CustomCaption(TypedDict):
    text: str | None
    inelinekeyboardmarkup: list[list[InlineKeyboardButton]] | None


class PyroHelper:
    """Helper class for additional Pyrogram functions."""

    @staticmethod
    async def get_channel_invites(client: Client, channels: list[int]) -> dict[str, ChannelInfo]:
        """
        Get invite links for a list of channels.

        Parameters:
            client (Client):
                Pyrogram client instance.
            channels (list[int]):
                List of channel IDs to get invite links for.

        Returns:
            dict[str, ChannelInfo]:
                Dictionary with channel titles as keys and ChannelInfo.

        Raises:
            ValueError:
                If any channel in the list does not have an invite link.

        """
        if not channels:
            return {}

        channels_n_invite: dict[str, ChannelInfo] = {}

        for channel_id in channels:
            channel = await client.get_chat(chat_id=channel_id)
            get_link = await client.invoke(
                raw.functions.messages.ExportChatInvite(  # type: ignore[reportPrivateImportUsage]
                    peer=await client.resolve_peer(peer_id=channel_id),  # type: ignore[reportArgumentType]
                    legacy_revoke_permanent=True,
                    request_needed=config.PRIVATE_REQUEST,
                ),
            )

            if get_link is not None:
                channel_invite = get_link.link  # type: ignore[reportAttributeAccessIssue]if channel.title not in channels_n_invite:
                channels_n_invite[channel.title] = ChannelInfo(
                    is_private=bool(channel.username is None),  # type: ignore[reportAttributeAccessIssue]
                    invite_link=channel_invite,
                    channel_id=channel_id,
                )

            else:
                raise NoInviteLinkError(channel_id)

        return channels_n_invite

    @staticmethod
    async def option_message(
        client: Client,
        message: Message,
        option_key: str | int,
        **kwargs: Any,  # noqa: ANN401
    ) -> Message | None:
        if isinstance(option_key, int):
            message_origin = await client.get_messages(chat_id=config.BACKUP_CHANNEL, message_ids=option_key)

            if message_origin:
                return cast("Message", await message_origin.copy(chat_id=message.chat.id, **kwargs))  # pyright: ignore[reportCallIssue]
        try:
            return await message.reply(
                text=str(option_key),
                **kwargs,
            )
        except UserIsBlocked:
            return None

    @staticmethod
    async def custom_caption(client: Client, option_key: str) -> CustomCaption:
        if isinstance(option_key, int):
            message_origin = await client.get_messages(chat_id=config.BACKUP_CHANNEL, message_ids=option_key)

            message = message_origin[0] if isinstance(message_origin, list) else message_origin

            return CustomCaption(
                text=message.text.markdown if message.text else None,
                inelinekeyboardmarkup=message.reply_markup.inline_keyboard
                if isinstance(message.reply_markup, InlineKeyboardMarkup)
                else None,
            )

        return CustomCaption(text=str(option_key), inelinekeyboardmarkup=None)
