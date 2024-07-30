import dns.resolver
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConfigurationError

from bot.config import config


class MongoDB:
    def __init__(self, name: str | None = None) -> None:
        try:
            self.client = AsyncIOMotorClient(host=str(config.MONGO_DB_URL))
        except ConfigurationError:
            dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
            dns.resolver.default_resolver.nameservers = ["8.8.8.8"]
            self.client = AsyncIOMotorClient(host=str(config.MONGO_DB_URL))
        self.db = self.client[name if name else config.MONGO_DB_NAME]

    async def add_user(self, user_id: int) -> bool:
        collection = self.db["Users"]
        result = await collection.update_one(
            filter={"_id": user_id},
            update={"$set": {"_id": user_id}},
            upsert=True,
        )
        return result.acknowledged

    async def add_file(self, file_link: str, file_origin: int, file_data: list[dict]) -> bool:
        collection = self.db["Files"]
        result = await collection.update_one(
            filter={"_id": file_link},
            update={
                "$set": {
                    "file_origin": file_origin,
                    "files": file_data,
                },
            },
            upsert=True,
        )
        return result.acknowledged

    async def delete_link_document(self, base64_file_link: str) -> bool:
        collection = self.db["Files"]
        result = await collection.delete_one(
            filter={"_id": base64_file_link},
        )
        return result.deleted_count > 0

    async def get_link_document(self, base64_file_link: str) -> dict | None:
        collection = self.db["Files"]
        pipeline = [{"$match": {"_id": base64_file_link}}]

        result = await collection.aggregate(pipeline).to_list(length=None)
        return result[0] if result else None

    async def get_user_ids(self) -> tuple[list[int], list[int]]:
        pipeline = [
            {"$project": {"_id": 1}},
            {"$group": {"_id": None, "user_ids": {"$addToSet": "$_id"}}},
            {"$project": {"_id": 0, "user_ids": 1}},
        ]

        users_collection = self.db["Users"]
        users_codex_collection = self.db["users"]

        user_ids_cursor = users_collection.aggregate(pipeline)
        user_ids = await user_ids_cursor.to_list(length=None)

        user_ids_codex_cursor = users_codex_collection.aggregate(pipeline)
        user_ids_codex = await user_ids_codex_cursor.to_list(length=None)

        main_ids = user_ids[0]["user_ids"] if user_ids else []
        codex_ids = user_ids_codex[0]["user_ids"] if user_ids_codex else []

        return (main_ids, codex_ids)

    async def stats(self) -> tuple[int, int]:
        link_count = await self.db["Files"].count_documents({})
        users_count = await self.db["Users"].count_documents({})
        return (link_count, users_count)

    async def cleanup_users(self, unsuccessful_ids: list, unsuccessful_ids_codex: list) -> None:
        """Cleans up users from database based on their IDs.

        Parameters:
            unsuccessful_ids (list): List of user unsuccessful id from teleshare to be delete from the database.
            unsuccessful_ids_codex (list): List of user unsuccessful id from CodeXbotz to be delete from the database.
        """
        if unsuccessful_ids:
            await self.db["Users"].delete_many({"_id": {"$in": unsuccessful_ids}})

        if unsuccessful_ids_codex:
            await self.db["users"].delete_many({"_id": {"$in": unsuccessful_ids_codex}})
