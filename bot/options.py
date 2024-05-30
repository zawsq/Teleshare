import dns.resolver
from pydantic import BaseModel
from pymongo.errors import ConfigurationError

from bot.config import config
from bot.database import MongoDB


class SettingsModel(BaseModel):
    FORCE_SUB_MESSAGE: str | int = "Please join the channel(s) first."
    START_MESSAGE: str | int = "I am a file-sharing bot."
    USER_REPLY_TEXT: str | int = "idk"

    AUTO_DELETE_MESSAGE: str = "This file(s) will be deleted within {} minutes"
    AUTO_DELETE_SECONDS: int = 300
    GLOBAL_MODE: bool = False
    BACKUP_FILES: bool = False


class InvalidValueError(Exception):
    def __init__(self, key: str | int) -> None:
        super().__init__(f"Value for key '{key}' must have the same type as the existing value.")


class Options:
    def __init__(self) -> None:
        """
        Initialize the Settings class.

        Parameters:
            self.settings:
                Initialized as SettingsModel.
            self.collection:
                The name of the collection.
            self.database:
                The MongoDB instance.
            self.document_id:
                The ID of the document to retrieve/update settings.
        """
        self.settings = SettingsModel()
        self.collection = "BotSettings"
        self.document_id = "MainOptions"
        try:
            self.database = MongoDB(database=config.MONGO_DB_NAME)
        except ConfigurationError:
            dns.resolver.default_resolver = dns.resolver.Resolver(configure=False)
            dns.resolver.default_resolver.nameservers = ["8.8.8.8"]
            self.database = MongoDB(database=config.MONGO_DB_NAME)

    async def load_settings(self) -> None:
        """
        Load settings from the MongoDB collection.

        Example:
            await self.load_settings()
        """
        pipeline = [{"$match": {"_id": self.document_id}}]
        settings_doc = await self.database.aggregate(collection=self.collection, pipeline=pipeline)

        if settings_doc:
            self.settings = SettingsModel(**settings_doc[0])
        else:
            self.settings = SettingsModel()

        update = {"$set": self.settings.model_dump()}
        db_filter = {"_id": self.document_id}

        await self.database.update_one(
            collection=self.collection,
            db_filter=db_filter,
            update=update,
        )

    async def update_settings(
        self,
        key: str,
        value: str | int,
    ) -> SettingsModel:
        """
        Update the settings and save them to the MongoDB collection.

        Parameters:
            key:
                The key/field name in the SettingsModel to update.
            value:
                The new value to set for the specified key.

        Returns:
            The updated SettingsModel instance from 'self.settings'.

        Raises:
            ValueError:
                If the provided key is not a valid field in the SettingsModel.
            ValidationError:
                Failed to validate changes.

        Example:
            await self.update_settings(key="START_MESSAGE", value="Hello, I am a bot.")
        """
        if key not in self.settings.__fields__:
            raise KeyError(key)

        annotation = self.settings.__fields__[key].annotation
        if annotation is not None and not isinstance(value, annotation):
            raise InvalidValueError(key)

        setattr(self.settings, key, value)
        self.settings = SettingsModel(**self.settings.model_dump())

        model_key, model_value = key, getattr(self.settings, key)

        db_filter = {"_id": self.document_id}
        update = {"$set": {model_key: model_value}}

        await self.database.update_one(
            collection=self.collection,
            db_filter=db_filter,
            update=update,
        )

        return self.settings


# create an instance
options = Options()
