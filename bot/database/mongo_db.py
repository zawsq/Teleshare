import dns.resolver
from async_lru import alru_cache
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConfigurationError

from bot.config import config

from .moderation import Moderation


class MongoDB(Moderation):
    """
    A class representing a MongoDB database connection.

    Parameters:
        name (str | None): The name of the database to connect to. Defaults to config.MONGO_DB_NAME.
    """

    def __init__(self, name: str | None = None) -> None:
        """
        Initializes the MongoDB connection.

        Raises:
            ConfigurationError: If the MongoDB connection configuration is invalid.
        """
        try:
            self.client = AsyncIOMotorClient(host=str(config.MONGO_DB_URL))
        except ConfigurationError:
            dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
            dns.resolver.default_resolver.nameservers = ["8.8.8.8"]
            self.client = AsyncIOMotorClient(host=str(config.MONGO_DB_URL))
        self.db = self.client[name if name else config.MONGO_DB_NAME]

    @alru_cache(maxsize=10, ttl=10)
    async def add_user(self, user_id: int) -> bool:
        """
        Adds a user to the database.

        Parameters:
            user_id (int): The ID of the user to add.

        Returns:
            bool: Whether the user was added successfully.
        """
        collection = self.db["Users"]
        result = await collection.update_one(
            filter={"_id": user_id},
            update={"$set": {"_id": user_id}},
            upsert=True,
        )
        return result.acknowledged

    async def add_file(self, file_link: str, file_origin: int, file_data: list[dict]) -> bool:
        """
        Adds a file to the database.

        Parameters:
            file_link (str): The link to the file.
            file_origin (int): The origin of the file.
            file_data (list[dict]): The data associated with the file.

        Returns:
            bool: Whether the file was added successfully.
        """
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
        """
        Deletes a link document from the database.

        Parameters:
            base64_file_link (str): The base64-encoded link to the file.

        Returns:
            bool: Whether the document was deleted successfully.
        """
        collection = self.db["Files"]
        result = await collection.delete_one(
            filter={"_id": base64_file_link},
        )
        return result.deleted_count > 0

    async def get_link_document(self, base64_file_link: str) -> dict | None:
        """
        Retrieves a link document from the database.

        Parameters:
            base64_file_link (str): The base64-encoded link to the file.

        Returns:
            dict | None: The document associated with the link, or None if not found.
        """
        collection = self.db["Files"]
        pipeline = [{"$match": {"_id": base64_file_link}}]

        result = await collection.aggregate(pipeline).to_list(length=None)
        return result[0] if result else None

    async def get_user_ids(self) -> tuple[list[int], list[int]]:
        """
        Retrieves the IDs of all users in the database.

        Returns:
            tuple[list[int], list[int]]: A tuple containing two lists of user IDs.
        """
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
        """
        Retrieves the number of links and users in the database.

        Returns:
            tuple[int, int]: A tuple containing the number of links and users.
        """
        link_count = await self.db["Files"].count_documents({})
        users_count = await self.db["Users"].count_documents({})
        return (link_count, users_count)

    async def cleanup_users(self, unsuccessful_ids: list, unsuccessful_ids_codex: list) -> None:
        """
        Cleans up users from the database based on their IDs.

        Parameters:
            unsuccessful_ids (list): List of user IDs to delete from the database.
            unsuccessful_ids_codex (list): List of user IDs to delete from the CodeXbotz database.
        """
        if unsuccessful_ids:
            await self.db["Users"].delete_many({"_id": {"$in": unsuccessful_ids}})

        if unsuccessful_ids_codex:
            await self.db["users"].delete_many({"_id": {"$in": unsuccessful_ids_codex}})
