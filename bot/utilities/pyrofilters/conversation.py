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

    CONVO_CACHE: ClassVar[set[int]] = set()

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
                cls.CONVO_CACHE.add(unique_id)
                return True

            if convo_stop is not None and text and unique_id in cls.CONVO_CACHE and text.startswith(convo_stop):
                message.convo_stop = True
                cls.CONVO_CACHE.discard(unique_id)
                return True

            if unique_id in cls.CONVO_CACHE:
                message.conversation = True
                return True

            return False

        return filters.create(func, "ConversationFilter")
