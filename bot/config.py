"""General configuration.

Config: Bot Config
"""

# ruff: noqa: ARG003
import logging
import sys
from pathlib import Path
<<<<<<< HEAD
from typing import Annotated

from pydantic import ValidationError
from pydantic.networks import UrlConstraints
from pydantic_core import MultiHostUrl
=======

from pydantic import MongoDsn, ValidationError
>>>>>>> 32724b27186ba0112bc1c6837f96340908682a3e
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

<<<<<<< HEAD
MongoSRVDsn = Annotated[MultiHostUrl, UrlConstraints(allowed_schemes=["mongodb+srv"])]
BASE_PATH = Path(__file__).parent.parent
=======
base_path = Path(__file__).parent.parent
>>>>>>> 32724b27186ba0112bc1c6837f96340908682a3e


class Config(BaseSettings):
    """A general configuration setup to read either .env or environment keys."""

    # Bot deploy config
    PORT: int = 8080
    HOSTNAME: str = "0.0.0.0"  # noqa: S104

    API_ID: int
    API_HASH: str
    BOT_TOKEN: str
<<<<<<< HEAD
    MONGO_DB_URL: MongoSRVDsn
=======
    MONGO_DB_URL: MongoDsn
>>>>>>> 32724b27186ba0112bc1c6837f96340908682a3e

    # Bot main config
    BACKUP_CHANNEL: int
    ROOT_ADMINS_ID: list[int]
    FORCE_SUB_CHANNELS: list[int]
    PRIVATE_REQUEST: bool = False

    model_config = SettingsConfigDict(
<<<<<<< HEAD
        env_file=f"{BASE_PATH}/.env",
=======
        env_file=f"{base_path}/.env",
>>>>>>> 32724b27186ba0112bc1c6837f96340908682a3e
    )

    @classmethod
    def settings_customise_sources(  # noqa: PLR0913
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            DotEnvSettingsSource(settings_cls),
            EnvSettingsSource(settings_cls),
        )


try:
    config = Config()  # pyright: ignore # noqa: PGH003
except ValidationError:
    logging.exception("Configuration Error")
    sys.exit()
