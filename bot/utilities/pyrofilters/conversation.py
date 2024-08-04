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
            return unique_id not in cls._convo_cache

        return filters.create(func, "ConversationFilter")

    @classmethod
    def create_conversation_filter(
        cls,
        convo_start: str | list | set,
        convo_stop: str | list | set | None = None,
    ) -> filters.Filter:
        """Create a filter function for a conversation.

        Parameters:
            convo_start (str | list | set):
                The starting text or texts for the conversation.
            convo_stop (str | list | set | None):
                The text or texts to stop the conversation. Defaults to None.

        Returns:
            filters.Filter:
                A filter function that can be used with Update Handlers.
        """

        async def func(flt: filters.Filter, client: Client, message: ConvoMessage) -> bool:  # noqa: ARG001
            text = message.text or message.caption
            unique_id = message.chat.id + message.from_user.id

            message.convo_start = False
            message.conversation = False
            message.convo_stop = False

            convo_start_check = convo_start if isinstance(convo_start, list | set) else [convo_start]

            if convo_stop is not None:
                convo_stop_check = convo_stop if isinstance(convo_stop, list | set) else [convo_stop]
            else:
                convo_stop_check = []

            if text and text in convo_start_check:
                message.convo_start = True
                cls._convo_cache.add(unique_id)
                return True

            if text and unique_id in cls._convo_cache and text in convo_stop_check:
                message.convo_stop = True
                cls._convo_cache.discard(unique_id)
                return True

            if unique_id in cls._convo_cache:
                message.conversation = True
                return True

            return False

        return filters.create(func, "ConversationFilter")
