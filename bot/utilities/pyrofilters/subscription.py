import datetime
from typing import ClassVar

import tzlocal
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message

from bot.config import config


class SubscriptionFilter:
    """
    A filter to check if a user is subscribed to the required channels.

    Attributes:
        SUBS_CACHE (ClassVar[dict[int, datetime.datetime]]): A cache to store user IDs and their last check time.
    """

    SUBS_CACHE: ClassVar[dict[int, datetime.datetime]] = {}

    @classmethod
    def subscription(cls) -> filters.Filter:
        """
        Creates a filter to check if a user is subscribed to the required channels.

        Returns:
            filters.Filter: A filter to check if a user is subscribed to the required channels.
        """

        async def func(flt: None, client: Client, message: Message) -> bool:  # noqa: ARG001
            """
            Checks if a user is subscribed to the required channels.

            Parameters:
                client (Client): The Pyrogram client.
                message (Message): The message to check.

            Returns:
                bool: True if the user is subscribed, False otherwise.
            """

            user_id = message.from_user.id
            status = [
                ChatMemberStatus.OWNER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.MEMBER,
            ]

            if user_id in config.ROOT_ADMINS_ID:
                return True

            if user_id in cls.SUBS_CACHE:
                user_cache_time = cls.SUBS_CACHE.get(user_id)
                current_time = datetime.datetime.now(tz=tzlocal.get_localzone())

                if user_cache_time is not None:
                    time_diff = current_time - user_cache_time
                    if time_diff <= datetime.timedelta(seconds=6):
                        return True

                cls.SUBS_CACHE.pop(user_id)

            try:
                for channel in config.FORCE_SUB_CHANNELS:
                    member = await client.get_chat_member(chat_id=channel, user_id=user_id)
                    if member.status not in status:
                        return False
            except UserNotParticipant:
                return False

            cls.SUBS_CACHE[user_id] = datetime.datetime.now(tz=tzlocal.get_localzone())
            return True

        return filters.create(func, "SubscriptionFilter")
