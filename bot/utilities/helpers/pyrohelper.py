from typing import Any, TypedDict, cast

from pyrogram import raw
from pyrogram.client import Client
from pyrogram.types import Message

from bot.config import config


class NoInviteLinkError(Exception):
    def __init__(self, channel: int | str) -> None:
        super().__init__(f"{channel} has no invite link")


class ChannelInfo(TypedDict):
    is_private: bool
    invite_link: str
    channel_id: int


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

        default = ChannelInfo(is_private=False, invite_link="invite link", channel_id=00000000)

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
                channel_invite = get_link.link  # type: ignore[reportAttributeAccessIssue]
                channels_n_invite.setdefault(channel.title, default).update(
                    ChannelInfo(
                        is_private=bool(channel.username is None),  # type: ignore[reportAttributeAccessIssue]
                        invite_link=channel_invite,
                        channel_id=channel_id,
                    ),
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
    ) -> Message:
        if isinstance(option_key, int):
            message_origin = await client.get_messages(chat_id=config.BACKUP_CHANNEL, message_ids=option_key)

            if message_origin:
                return cast(Message, await message_origin.copy(chat_id=message.chat.id, **kwargs))  # pyright: ignore[reportCallIssue]

        return await message.reply(
            text=str(option_key),
            **kwargs,
        )
