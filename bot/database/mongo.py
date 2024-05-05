from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import InvalidOperation
from pymongo.results import DeleteResult, UpdateResult

from bot.config import config


class MongoDB:
    """Establish a connection to a MongoDB.

    Parameters:
        database (str): The name of the database to connect to.

    Attributes:
        client (AsyncIOMotorClient): The Motor client connected to the MongoDB server.
        db (Database): The database object representing the connected database.

    """

    def __init__(self, database: str) -> None:
        self.client = AsyncIOMotorClient(host=str(config.MONGO_DB_URL))
        self.db = self.client[database]

    async def delete_one(
        self,
        collection: str,
        db_filter: dict[str, Any],
    ) -> DeleteResult:
        """Delete a single document from a MongoDB collection.

        This method deletes the first document that matches the `db_filter``.

        Parameters:
            collection (str): The name of the collection to delete from.
            db_filter (dict[str, str]): The filter to match the document to delete.

        Returns:
            DeleteResult: The result of the delete operation.

        """
        _collection = self.db[collection]
        return await _collection.delete_one(filter=db_filter)

    async def delete_many(
        self,
        collection: str,
        db_filter: dict[str, Any],
    ) -> DeleteResult:
        """Delete multiple documents from a MongoDB collection.

        This method deletes all documents that match the `db_filter`.

        Parameters:
            collection (str): The name of the collection to delete from.
            db_filter (dict[str, Any]): The filter to match the documents to delete.

        Returns:
            DeleteResult: The result of the delete operation.

        """
        _collection = self.db[collection]
        return await _collection.delete_many(filter=db_filter)

    async def update_one(
        self,
        collection: str,
        db_filter: dict[str, str],
        update: dict[str, str],
        upsert: bool = True,  # noqa: FBT001, FBT002
    ) -> UpdateResult:
        """Update a single document in a MongoDB collection.

        This method updates a single document that matches the `db_filter`.
        The `update` argument specifies the modifications to apply.

        Parameters:
            collection (str): The name of the collection to update.
            db_filter (dict[str, str]): The filter to match the document to update.
            update (dict[str, str]): The update operations to apply.
            upsert (bool, optional): If True, inserts a new document if no match is found.
                Defaults to True.

        Returns:
            UpdateResult: The result of the update operation.

        """
        _collection = self.db[collection]
        return await _collection.update_one(
            filter=db_filter,
            update=update,
            upsert=upsert,
        )

    async def aggregate(
        self,
        collection: str,
        pipeline: list[dict[str, Any]],
    ) -> list[dict]:
        """Perform aggregation on documents in a MongoDB collection.

        Aggregation allows you to perform efficient data processing..

        Reference:
            https://docs.mongodb.com/manual/aggregation/

        Parameters:
            collection (str): The name of the collection to perform aggregation on.
            pipeline (list[dict[str, str]]): A list of aggregation pipeline operations to apply.

        Returns:
            list[dict]: The aggregated results.

        Raises:
            ValueError: If an invalid pipeline operation is provided.

        """
        _collection = self.db[collection]
        try:
            cursor = _collection.aggregate(pipeline=pipeline)
            return [doc async for doc in cursor]
        except InvalidOperation as e:
            raise ValueError(e) from e
