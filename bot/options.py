from pydantic import BaseModel

from .database import MongoDB
from .database.models import FltId, PipeMatch, UpdSet


class SettingsModel(BaseModel):
    FORCE_SUB_MESSAGE: str = "Please join the channel(s) first."

    START_MESSAGE: str = "I am a file-sharing bot."
    CUSTOM_CAPTION: str = "This file(s) will be deleted within {} minutes"
    USER_REPLY_TEXT: str = "idk"

    AUTO_DELETE_SECONDS: int = 300


class Options:
    def __init__(self) -> None:
        """
        Initialize the Settings class.

        Parameters:
            self.settings:
                Initialized as None.
            self.collection:
                The name of the collection.
            self.database:
                The MongoDB instance.
            self.document_id:
                The ID of the document to retrieve/update settings.
        """
        self.settings = SettingsModel
        self.collection = "BotSettings"
        self.database = MongoDB("Zaws-File-Share")
        self.document_id = "MainOptions"

    async def load_settings(self) -> None:
        """
        Load settings from the MongoDB collection.

        Example:
            await self.load_settings()
        """
        match = PipeMatch(match=FltId(_id=self.document_id).model_dump())
        pipeline = [match.model_dump()]
        settings_doc = await self.database.aggregate(collection=self.collection, pipeline=pipeline)

        if settings_doc:
            self.settings = SettingsModel(**settings_doc[0])
        else:
            db_filter = FltId(_id=self.document_id).model_dump()
            update = UpdSet(
                _set=SettingsModel().model_dump(),
            ).model_dump()

            set_default = await self.database.update_one(
                collection=self.collection,
                db_filter=db_filter,
                update=update,
            )
            if set_default.acknowledged:
                self.settings = SettingsModel()

    async def update_settings(
        self,
        key: str,
        value: list[int | str] | str | int,
    ) -> SettingsModel | None:
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
        # Change self.settings key value
        setattr(self.settings, key, value)
        model_key, model_value = key, getattr(self.settings, key)

        # Validate Changes
        self.settings = SettingsModel(**self.settings.model_dump())

        db_filter = FltId(_id=self.document_id).model_dump()
        update = UpdSet(_set={model_key: model_value}).model_dump()

        await self.database.update_one(
            collection=self.collection,
            db_filter=db_filter,
            update=update,
        )

        return self.settings


# create an instance
options = Options()
