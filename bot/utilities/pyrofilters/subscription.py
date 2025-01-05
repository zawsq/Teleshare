import datetime
from typing import ClassVar

import tzlocal
from lru import LRU
from pyrogram import filters
from pyrogram.client import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message

from bot.config import config
from bot.database import MongoDB

database = MongoDB()


class SubscriptionMessage(Message):
    def __init__(self) -> None:
        self.user_is_banned = False


class SubscriptionFilter:
    """
    A filter to check if a user is subscribed to the required channels.

    Attributes:
        CACHE_USER_SECONDS (int): Amount of seconds before checking the user again to avoid spams.
        _subs_cache (ClassVar[LRU[int, datetime.datetime]]): A lru dict to store user IDs and their last check time.
    """

    CACHE_USER_SECONDS: int = 15
    _subs_cache: ClassVar[LRU] = LRU(10)

    @classmethod
    def subscription(cls) -> filters.Filter:
        """
        Creates a filter to check if a user is subscribed to the required channels.

        Returns:
            filters.Filter: A filter to check if a user is subscribed to the required channels.
        """

        async def func(flt: None, client: Client, message: SubscriptionMessage) -> bool:  # noqa: ARG001
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

            if user_id in config.ROOT_ADMINS_ID or not config.FORCE_SUB_CHANNELS:
                return True

            if await database.is_user_banned(user_id):
                message.user_is_banned = True
                return False

            if user_id in cls._subs_cache:
                user_cache_time = cls._subs_cache.get(user_id)
                current_time = datetime.datetime.now(tz=tzlocal.get_localzone())

                if user_cache_time and (current_time - user_cache_time) <= datetime.timedelta(
                    seconds=cls.CACHE_USER_SECONDS,
                ):
                    return True

                cls._subs_cache.pop(user_id)

            try:
                for channel in config.FORCE_SUB_CHANNELS:
                    member = await client.get_chat_member(chat_id=channel, user_id=user_id)
                    if member.status not in status:
                        return False
            except UserNotParticipant:
                return False

            cls._subs_cache[user_id] = datetime.datetime.now(tz=tzlocal.get_localzone())
            return False

        return filters.create(func, "SubscriptionFilter")
