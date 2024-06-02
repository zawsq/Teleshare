import asyncio
import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import ClassVar

from lru import LRU
from pyrogram.client import Client
from pyrogram.types import Message


class RateLimiter:
    """
    A experimental pyrogram rate limiter which use to limit sending messages to chats.

    Attributes:
        MAX_EXECUTIONS_PER_SECOND_BULK (ClassVar[int]):
            The maximum number of executions per second for bulk notifications.
        MAX_EXECUTIONS_PER_MINUTE_SAME_CHAT (ClassVar[int]):
            The maximum number of executions per minute for the same chat ID.
        chat_execution_counts (ClassVar[LRU]):
            A lru dictionary to store the execution counts for each chat ID.
        last_second_reset (ClassVar[float]):
            The time of the last second reset.
        last_minute_reset (ClassVar[float]):
            The time of the last minute reset.
    """

    logger = logging.getLogger(__name__)

    MAX_EXECUTIONS_PER_SECOND_BULK: ClassVar[int] = 40
    MAX_EXECUTIONS_PER_MINUTE_SAME_CHAT: ClassVar[int] = 30

    chat_execution_counts: ClassVar[LRU] = LRU(MAX_EXECUTIONS_PER_MINUTE_SAME_CHAT)
    last_second_reset: ClassVar[float] = time.perf_counter()
    last_minute_reset: ClassVar[float] = time.perf_counter()

    @classmethod
    def hybrid_limiter(cls, func_count: int = 1) -> Callable[[Callable], Callable]:
        """
        A hybrid rate limiter decorator.

        Parameters:
            func_count (int):
                The number of function executions to count. Defaults to 1.
                If your function sends 2 message set to 2.

        Returns:
            Callable[[Callable], Callable]: A decorator function.
        """

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(client: Client, message: Message, *args: list, **kwargs: list) -> bool:
                """
                The decorated function.

                Parameters:
                    client (Client): The Pyrogram client.
                    message (Message): The Pyrogram message.

                Returns:
                    bool: The result of the function execution.
                """

                chat_id = message.chat.id
                while True:
                    now = time.perf_counter()
                    elapsed_time_second = now - cls.last_second_reset
                    elapsed_time_minute = now - cls.last_minute_reset

                    if elapsed_time_second >= 1:
                        cls.last_second_reset = now

                    if elapsed_time_minute >= 60:  # noqa: PLR2004
                        cls.chat_execution_counts.clear()
                        cls.last_minute_reset = now
                    else:
                        elapsed_time_minute %= 60

                    if chat_id not in cls.chat_execution_counts:
                        cls.chat_execution_counts[chat_id] = 0

                    if cls.chat_execution_counts[chat_id] < cls.MAX_EXECUTIONS_PER_MINUTE_SAME_CHAT:
                        cls.chat_execution_counts[chat_id] += func_count

                        if sum(cls.chat_execution_counts.values()) <= cls.MAX_EXECUTIONS_PER_SECOND_BULK:
                            return await func(client, message, *args, **kwargs)

                    wait_time_second = 1 - elapsed_time_second
                    wait_time_minute = 60 - elapsed_time_minute
                    sleep_time = max(wait_time_second, wait_time_minute)
                    cls.logger.info("Waiting for %d seconds... before next execution", sleep_time)

                    await asyncio.sleep(max(wait_time_second, wait_time_minute))

            return wrapper

        return decorator
