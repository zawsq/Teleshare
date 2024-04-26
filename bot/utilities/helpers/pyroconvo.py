# ruff: noqa: ARG001

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

    def __init__(self) -> None:
        self.cache = set()

    def stop_conversation(self, unique_id: int) -> None:
        """Manually stop conversation.

        Parameters:
            unique_id (int):
                Unique id with combination of chat id and user id

        Returns:
            None
        """
        self.cache.discard(unique_id)

    def create_conversation_filter(
        self,
        convo_start: str,
        convo_stop: str | None,
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

        async def func(flt: filters.Filter, client: Client, message: ConvoMessage) -> bool:
            text = message.text or message.caption
            unique_id = message.chat.id + message.from_user.id
            message.convo_start = False
            message.convo_stop = False
            message.conversation = False

            if text and text.startswith(convo_start):
                message.convo_start = True
                self.cache.add(unique_id)
                return True

            if convo_stop is not None and text and unique_id in self.cache and text.startswith(convo_stop):
                message.convo_stop = True
                self.cache.discard(unique_id)
                return True

            if unique_id in self.cache:
                message.conversation = True
                return True

            return False

        return filters.create(func, "ConversationFilter")
