from pydantic import BaseModel

from bot.database import MongoDB


class SettingsModel(BaseModel):
    """
    A model representing the bot's settings.

    Parameters:
        FORCE_SUB_MESSAGE (str | int): The message to display when a user is not subscribed.
        START_MESSAGE (str | int): The message to display when a user starts the bot.
        USER_REPLY_TEXT (str | int): The text to reply to a user.
        AUTO_DELETE_MESSAGE (str | int): The message to display when a file is deleted.
        AUTO_DELETE_SECONDS (int): The number of seconds to wait before deleting a file.
        GLOBAL_MODE (bool): Whether the bot is in global mode.
        BACKUP_FILES (bool): Whether to backup files.
    """

    FORCE_SUB_MESSAGE: str | int = "Please join the channel(s) first."
    BANNED_USER_MESSAGE: str = "You have been banned from using this bot."
    START_MESSAGE: str | int = "I am a file-sharing bot."
    USER_REPLY_TEXT: str | int = "idk"
    AUTO_DELETE_MESSAGE: str | int = "This file(s) will be deleted within {} minutes"
    AUTO_DELETE_SECONDS: int = 300
    GLOBAL_MODE: bool = False
    BACKUP_FILES: bool = True


class InvalidValueError(Exception):
    """
    An exception raised when a value is invalid.

    Parameters:
        key (str | int): The key that has an invalid value.
    """

    def __init__(self, key: str | int) -> None:
        super().__init__(f"Value for key '{key}' must have the same type as the existing value.")


class Options(MongoDB):
    """
    A class representing the bot's options.

    Parameters:
        self.settings (SettingsModel): The bot's settings.
        self.collection (str): The name of the collection.
        self.document_id (str): The ID of the document to retrieve/update settings.
    """

    def __init__(self) -> None:
        super().__init__()
        self.settings = SettingsModel()
        self.collection = "BotSettings"
        self.document_id = "MainOptions"

    async def load_settings(self) -> None:
        """
        Load settings from the MongoDB collection.

        Example:
            await self.load_settings()
        """
        pipeline = [{"$match": {"_id": self.document_id}}]
        cursor = self.db[self.collection].aggregate(pipeline)
        settings_doc = await cursor.to_list(length=None)

        if settings_doc:
            self.settings = SettingsModel(**settings_doc[0])
        else:
            self.settings = SettingsModel()

        update = {"$set": self.settings.model_dump()}
        db_filter = {"_id": self.document_id}
        await self.db[self.collection].update_one(
            filter=db_filter,
            update=update,
            upsert=True,
        )

    async def update_settings(self, key: str, value: str | int) -> SettingsModel:
        """
        Update the settings and save them to the MongoDB collection.

        Parameters:
            key (str): The key/field name in the SettingsModel to update.
            value (str | int): The new value to set for the specified key.

        Returns:
            The updated SettingsModel instance from 'elf.settings'.

        Raises:
            KeyError:
                If the provided key is not a valid field in the SettingsModel.
            InvalidValueError:
                If the provided value is not of the same type as the existing value.

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
        await self.db[self.collection].update_one(
            filter=db_filter,
            update=update,
            upsert=True,
        )
        return self.settings


# create an instance
options = Options()
