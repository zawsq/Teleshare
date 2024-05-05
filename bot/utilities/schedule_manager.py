import datetime

import tzlocal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from pyrogram.client import Client


class ScheduleManager:
    def __init__(self) -> None:
        self.bot_client = ""
        self.scheduler = AsyncIOScheduler(
            timezone=tzlocal.get_localzone(),
            misfire_grace_time=5,
        )

    async def start(self) -> None:
        self.scheduler.start()

    async def delete_messages(self, client: Client, chat_id: int, message_ids: list[int]) -> None:
        await client.delete_messages(chat_id=chat_id, message_ids=message_ids)

    async def schedule_delete(
        self,
        client: Client,
        chat_id: int,
        message_ids: list[int],
        delete_n_seconds: int,
    ) -> None:
        now = datetime.datetime.now(tz=tzlocal.get_localzone())
        self.scheduler.add_job(
            func=self.delete_messages,
            trigger="date",
            run_date=now + datetime.timedelta(seconds=delete_n_seconds),
            args=[client, chat_id, message_ids],
        )


schedule_manager = ScheduleManager()
