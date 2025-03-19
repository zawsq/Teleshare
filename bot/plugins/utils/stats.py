from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import Message
import time  # Import time untuk menghitung uptime
import asyncio

from bot.database import MongoDB
from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrofilters import PyroFilters
from bot.utilities.pyrotools import HelpCmd

database = MongoDB()

# Menyimpan waktu mulai bot
START_TIME = time.time()

@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("stats"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def stats(client: Client, message: Message) -> Message:
    """A command to display links and users count, ping, and uptime.:

    **Usage:**
        /stats
    """

    link_count, users_count = await database.stats()

    # Menghitung uptime
    uptime = time.time() - START_TIME

    # Menghitung hari, jam, menit, dan detik
    days = int(uptime // (24 * 3600))
    hours = int((uptime % (24 * 3600)) // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)

    uptime_str = f"{days} days {hours} hours {minutes} minutes {seconds} seconds"

    # Mengukur ping
    start_time = time.time()
    ping_test_message = await message.reply("Ping test")  # Mengirim pesan untuk mengukur waktu
    ping_time = time.time() - start_time  # Hitung waktu ping
    await asyncio.sleep(2)
    await client.delete_messages(chat_id=message.chat.id, message_ids=ping_test_message.id)  # Hapus pesan ping test

    # Kirim pesan baru dengan informasi
    stats_message = await message.reply(
        f">STATS:\n"
        f"**Users Count:** `{users_count}`\n"
        f"**Links Count:** `{link_count}`\n\n"
        f"✦•┈๑⋅⋯ ⋯⋅๑┈•✦\n"
        f"**Ping:** `{ping_time * 1000:.2f} ms`\n"
        f"**Uptime:**\n`{uptime_str}`\n"
        f"✦•┈๑⋅⋯ ⋯⋅๑┈•✦\n",  # Mengonversi ke milidetik
    )

    # Tunggu selama 30 detik sebelum menghapus pesan
    await asyncio.sleep(30)
    await client.delete_messages(chat_id=message.chat.id, message_ids=stats_message.id)

HelpCmd.set_help(
    command="stats",
    description=stats.__doc__,
    allow_global=False,
    allow_non_admin=False,
)
