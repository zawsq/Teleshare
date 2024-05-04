# ruff: noqa: ARG001

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from pyrogram.types import Message

from bot.config import config


class SubscriptionFilter:
    @staticmethod
    def subscription() -> filters.Filter:
        async def func(flt: None, client: Client, message: Message) -> bool:
            user_id = message.from_user.id
            status = [
                ChatMemberStatus.OWNER,
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.MEMBER,
            ]

            if user_id in config.ROOT_ADMINS_ID:
                return True

            try:
                for channel in config.FORCE_SUB_CHANNELS:
                    member = await client.get_chat_member(chat_id=channel, user_id=user_id)
                    if member.status not in status:
                        return False
            except UserNotParticipant:
                return False
            return True

        return filters.create(func, "SubscriptionFilter")
