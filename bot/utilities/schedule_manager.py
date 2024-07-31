import datetime

import tzlocal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.client import Client


class ScheduleManager:
    """
    Manages scheduling of tasks for a Pyrogram client.

    Attributes:
        scheduler (AsyncIOScheduler): The scheduler instance.
    """

    def __init__(self) -> None:
        """
        Initializes the ScheduleManager instance.
        """
        self.scheduler = AsyncIOScheduler(
            timezone=tzlocal.get_localzone(),
            misfire_grace_time=5,
        )

    async def start(self) -> None:
        """
        Starts the scheduler.
        """
        self.scheduler.start()

    async def delete_messages(self, client: Client, chat_id: int, message_ids: list[int]) -> None:
        """
        Deletes messages from a chat.

        Parameters:
            client (Client): The Pyrogram client instance.
            chat_id (int): The chat ID.
            message_ids (list[int]): The list of message IDs to delete.
        """
        await client.delete_messages(chat_id=chat_id, message_ids=message_ids)

    async def schedule_delete(
        self,
        client: Client,
        chat_id: int,
        message_ids: list[int],
        delete_n_seconds: int,
    ) -> None:
        """
        Schedules a message deletion task.

        Parameters:
            client (Client): The Pyrogram client instance.
            chat_id (int): The chat ID.
            message_ids (list[int]): The list of message IDs to delete.
            delete_n_seconds (int): The number of seconds to wait before deleting.
        """
        now = datetime.datetime.now(tz=tzlocal.get_localzone())
        self.scheduler.add_job(
            func=self.delete_messages,
            trigger="date",
            run_date=now + datetime.timedelta(seconds=delete_n_seconds),
            args=[client, chat_id, message_ids],
        )


schedule_manager = ScheduleManager()
