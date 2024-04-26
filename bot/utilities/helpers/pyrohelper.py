from pyrogram.client import Client
from pyrogram.types import Chat


class NoInviteLinkError(Exception):
    def __init__(self, channel: int | str) -> None:
        super().__init__(f"{channel} has no invite link")


class PyroHelper:
    """Helper class for additional Pyrogram functions."""

    @staticmethod
    async def get_channel_invites(client: Client, channels: list[int]) -> dict[str, int]:
        """
        Get invite links for a list of channels.

        Parameters:
            client (Client):
                Pyrogram client instance.
            channels (list[int]):
                List of channel IDs to get invite links for.

        Returns:
            dict[str, int]:
                Dictionary with channel titles as keys and their invite links as values.

        Raises:
            ValueError:
                If any channel in the list does not have an invite link.

        Example:
            make sure the bot have required permissions to get invites
            >>> from pyrogram import Client
            >>> from pyrohelper import PyroHelper

            >>> app = Client("session_name")
            >>> helper = PyroHelper()

            >>> channels = [123456789, 987654321]
            >>> invite_links = await helper.get_channel_invites(app, channels)
            >>> print(invite_links)
            {
                "Channel Title 1": "https://t.me/joinchat/ABCDE...",
                "Channel Title 2": "https://t.me/joinchat/FGHIJ..."
            }
        """
        channels_n_invite = {}
        for channel_id in channels:
            channel = await client.get_chat(chat_id=channel_id)
            if isinstance(channel, Chat):
                invite_link = channel.invite_link
            else:
                invite_link = await client.export_chat_invite_link(channel_id)
            channels_n_invite[channel.title] = invite_link

        return channels_n_invite
