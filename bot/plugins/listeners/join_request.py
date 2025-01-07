from pyrogram.client import Client
from pyrogram.types import ChatJoinRequest

from bot.config import config
from bot.database import MongoDB

database = MongoDB()


@Client.on_chat_join_request()
async def join_request(client: Client, chat_join_request: ChatJoinRequest) -> bool | None:  # noqa: ARG001
    if config.PRIVATE_REQUEST:
        return await database.user_join_request(
            user_id=chat_join_request.from_user.id,
            channel_id=chat_join_request.chat.id,
        )
    return None
