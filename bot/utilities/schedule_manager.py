import datetime

import tzlocal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


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

    async def delete_messages(
        self,
        client: Client,
        chat_id: int,
        message_ids: list[int],
        base64_file_link: str,
    ) -> None:
        """
        Deletes messages from a chat.

        Parameters:
            client (Client): The Pyrogram client instance.
            chat_id (int): The chat ID.
            message_ids (list[int]): The list of message IDs to delete.
        """
        chunk_size = 100
        chunked_ids = [message_ids[i : i + chunk_size] for i in range(0, len(message_ids), chunk_size)]

        for i in chunked_ids:
            await client.delete_messages(chat_id=chat_id, message_ids=i)

        link = f"https://t.me/{client.me.username}?start={base64_file_link}"  # type: ignore[reportOptionalMemberAccess]
        retrieve_files = [[InlineKeyboardButton(text="Deleted File(s)", url=link)]]

        await client.send_message(
            chat_id=chat_id,
            text="Retrieve Deleted File(s)",
            reply_markup=InlineKeyboardMarkup(retrieve_files),
        )

    async def schedule_delete(
        self,
        client: Client,
        chat_id: int,
        message_ids: list[int],
        delete_n_seconds: int,
        base64_file_link: str,
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
            args=[client, chat_id, message_ids, base64_file_link],
        )


schedule_manager = ScheduleManager()
