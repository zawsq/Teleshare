import asyncio
import logging
import sys
import threading

from pyrogram.client import Client
from pyrogram.errors import ChannelInvalid, ChatAdminRequired
from pyrogram.sync import idle
from rich.logging import RichHandler
from rich.traceback import install

from bot.config import config
from bot.options import options
from bot.utilities.helpers import NoInviteLinkError, PyroHelper, RateLimiter
from bot.utilities.http_server import HTTPServer
from bot.utilities.schedule_manager import schedule_manager

install(show_locals=True)

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()],
)

background_tasks = set()


async def main() -> None:
    bot_client = Client(
        name=config.BOT_SESSION,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        bot_token=config.BOT_TOKEN,
        workers=config.BOT_WORKER,
        plugins={"root": f"{__package__}/plugins" if __package__ else "plugins"},
        max_message_cache_size=config.BOT_MAX_MESSAGE_CACHE_SIZE,
    )

    # Load database settings
    await options.load_settings()
    await bot_client.start()
    # Bot setup
    try:
        channels_n_invite = await PyroHelper.get_channel_invites(client=bot_client, channels=config.FORCE_SUB_CHANNELS)
        bot_client.channels_n_invite = channels_n_invite  # pyright: ignore[reportAttributeAccessIssue]
    except (ChannelInvalid, ChatAdminRequired, NoInviteLinkError) as e:
        sys.exit(f"Please add and give me permission in FORCE_SUB_CHANNELS and BACKUP_CHANNEL:\n{e}")

    await schedule_manager.start()

    task = None
    if config.HTTP_SERVER:
        http_server = HTTPServer(host=config.HOSTNAME, port=config.PORT)
        task = asyncio.create_task(http_server.run_server())
        background_tasks.add(task)
    if config.RATE_LIMITER:
        thread = threading.Thread(target=RateLimiter.cooldown_limiter)
        thread.daemon = True
        thread.start()

    await idle()

    if task:
        task.add_done_callback(background_tasks.discard)

    await bot_client.stop()


asyncio.run(main())
