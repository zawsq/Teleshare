import asyncio
import logging
import time
from collections.abc import Callable
from functools import wraps
from typing import ClassVar

from lru import LRU
from pyrogram.client import Client
from pyrogram.types import Message

from bot.config import config


class RateLimiter:
    """
    A experimental pyrogram rate limiter which use to limit the amount of update or command that bot handles.

    Attributes:
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

    MAX_EXECUTIONS_PER_MINUTE_SAME_CHAT: ClassVar[int] = 25

    chat_execution_counts: ClassVar[LRU] = LRU(100)

    last_second_reset: ClassVar[float] = time.perf_counter()
    last_minute_reset: ClassVar[float] = time.perf_counter()

    @classmethod
    def cooldown_limiter(cls) -> None:
        """
        Used to update every minute with new time and chat_execution_counts per id.
        Moves queue to execs for rate limiter.
        Deletes the key if there's nothing to execute or queue.
        Should only be runned once during startup."""
        exec_per_min = cls.MAX_EXECUTIONS_PER_MINUTE_SAME_CHAT
        cls.logger.info("cooldown_limiter Started...")

        while True:
            current_time = time.perf_counter()
            if current_time - cls.last_minute_reset >= 60:  # noqa: PLR2004
                cls.last_minute_reset = current_time
                for key, value in cls.chat_execution_counts.items():
                    queue = value.get("queue", 0)
                    execs, new_queue = (queue, 0) if queue <= exec_per_min else (exec_per_min, queue - exec_per_min)

                    if execs == 0 and new_queue == 0:
                        cls.chat_execution_counts.pop(key)
                    else:
                        cls.chat_execution_counts.update({key: {"exec": execs, "queue": new_queue}})
            time.sleep(2)

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
            async def wrapper(client: Client, message: Message, *args: tuple, **kwargs: dict) -> bool:
                """
                The decorated function.

                Parameters:
                    client (Client): The Pyrogram client.
                    message (Message): The Pyrogram message.

                Returns:
                    bool: The result of the function execution.
                """

                if not config.RATE_LIMITER:
                    return await func(client, message, *args, **kwargs)

                chat_id = message.chat.id

                cls.chat_execution_counts.setdefault(chat_id, {"exec": 0, "queue": 0})

                user_dict = cls.chat_execution_counts[chat_id]
                now = time.perf_counter()
                elapsed_time_minute = now - cls.last_minute_reset

                if user_dict["exec"] >= cls.MAX_EXECUTIONS_PER_MINUTE_SAME_CHAT:
                    cls.chat_execution_counts[chat_id]["queue"] += func_count

                    sleep_time = 60
                    sleep_queue = (user_dict["queue"] // cls.MAX_EXECUTIONS_PER_MINUTE_SAME_CHAT) + 1

                    total_sleep = (sleep_time * sleep_queue) - elapsed_time_minute

                    cls.logger.info("Waiting for %d seconds... before next execution, id: %d", total_sleep, chat_id)
                    await asyncio.sleep(total_sleep)

                cls.chat_execution_counts.setdefault(chat_id, {"exec": 0, "queue": 0})["exec"] += func_count

                return await func(client, message, *args, **kwargs)

            return wrapper

        return decorator
