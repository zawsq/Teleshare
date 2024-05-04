# ruff: noqa: ARG001

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message

from bot.config import config
from bot.options import options


class AdminsFilter:
    @staticmethod
    def admin(
        allow_global: bool = False,  # noqa: FBT001, FBT002
    ) -> filters.Filter:
        async def func(flt: None, client: Client, message: Message) -> bool:
            user_id = message.from_user.id
            is_global = options.settings.IS_GLOBAL
            if user_id in config.ROOT_ADMINS_ID or allow_global and is_global:
                return True

            return False

        return filters.create(func, "SubscriptionFilter")
