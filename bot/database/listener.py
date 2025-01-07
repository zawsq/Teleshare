from motor.motor_asyncio import AsyncIOMotorDatabase


class Listener:
    db: AsyncIOMotorDatabase

    async def user_join_request(self, user_id: int, channel_id: int) -> bool:
        """
        Adds a private channel to the user's list of channels in the database.

        Parameters:
            user_id (int): The ID of the user.
            channel_id (int): The ID of the channel to add.

        Returns:
            bool: Whether the operation was successful.
        """
        collection = self.db["Users"]
        result = await collection.update_one(
            filter={"_id": user_id},
            update={"$addToSet": {"channels": channel_id}},
            upsert=True,
        )

        return result.acknowledged

    async def user_requested_channels(self, user_id: int) -> list:
        """
        Fetches the list of channels for the user from the database.

        Parameters:
            user_id (int): The ID of the user.

        Returns:
            list: The list of private channel IDs the user is part of.
        """
        collection = self.db["Users"]
        user_data = await collection.find_one({"_id": user_id}, {"_id": 0, "channels": 1})
        return user_data.get("channels", []) if user_data else []
