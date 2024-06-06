from typing import ClassVar

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message


class ConvoMessage(Message):
    def __init__(self) -> None:
        self.convo_start = False
        self.convo_stop = False
        self.conversation = False


class ConversationFilter:
    """Experimental pyrogram add-on conversation filter."""

    _convo_cache: ClassVar[set[int]] = set()

    @classmethod
    def user_not_in_conversation(cls) -> filters.Filter:
        """Create a filter function for the given check_on_convo.

        Returns:
            filters.Filter:
                A filter function that can be used with Update Handlers
        """

        async def func(flt: filters.Filter, client: Client, message: Message) -> bool:  # noqa: ARG001
            """Checks if user is currently in conversation."""
            unique_id = message.chat.id + message.from_user.id

            if unique_id in cls._convo_cache:
                return False

            return True

        return filters.create(func, "ConversationFilter")

    @classmethod
    def create_conversation_filter(
        cls,
        convo_start: str,
        convo_stop: str | None = None,
    ) -> filters.Filter:
        """Create a filter function for the given convo_start.

        Parameters:
            convo_start (str):
                The starting text for the conversation.
            convo_stop (str, optional):
                The text to stop the conversation. Defaults to None.

        Returns:
            filters.Filter:
                A filter function that can be used with Update Handlers
        """

        async def func(flt: filters.Filter, client: Client, message: ConvoMessage) -> bool:  # noqa: ARG001
            text = message.text or message.caption
            unique_id = message.chat.id + message.from_user.id

            message.convo_start = False
            message.conversation = False
            message.convo_stop = False

            if text and text.startswith(convo_start):
                message.convo_start = True
                cls._convo_cache.add(unique_id)
                return True

            if convo_stop is not None and text and unique_id in cls._convo_cache and text.startswith(convo_stop):
                message.convo_stop = True
                cls._convo_cache.discard(unique_id)
                return True

            if unique_id in cls._convo_cache:
                message.conversation = True
                return True

            return False

        return filters.create(func, "ConversationFilter")
