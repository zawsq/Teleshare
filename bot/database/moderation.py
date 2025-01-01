from async_lru import alru_cache
from motor.motor_asyncio import AsyncIOMotorDatabase


class Moderation:
    db: AsyncIOMotorDatabase

    async def ban_user(self, user_id: int) -> bool:
        """
        Bans a user in the database.

        Parameters:
            user_id (int): The ID of the user to ban.

        Returns:
            bool: Whether the user was successfully banned.
        """
        collection = self.db["Users"]
        result = await collection.update_one(
            filter={"_id": user_id},
            update={"$set": {"_id": user_id, "banned": True}},
            upsert=False,
        )

        return bool(result.matched_count)

    async def unban_user(self, user_id: int) -> bool:
        """
        Unbans a user in the database.

        Parameters:
            user_id (int): The ID of the user to unban.

        Returns:
            bool: Whether the user was successfully unbanned.
        """
        collection = self.db["Users"]
        result = await collection.update_one(
            filter={"_id": user_id},
            update={"$set": {"_id": user_id, "banned": False}},
            upsert=False,
        )
        return bool(result.matched_count)

    @alru_cache(maxsize=69, ttl=15)
    async def is_user_banned(self, user_id: int) -> bool:
        """
        Checks if a user is banned in the database.

        Parameters:
            user_id (int): The ID of the user to check.

        Returns:
            bool: True if the user is banned, False otherwise.
        """
        collection = self.db["Users"]
        user = await collection.find_one({"_id": user_id}, {"_id": 0, "banned": 1})

        return user.get("banned", False) if user else False
