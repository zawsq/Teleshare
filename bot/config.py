"""General configuration.

Config: Bot Config
"""

# ruff: noqa: ARG003
import logging
import sys
from pathlib import Path

from pydantic import MongoDsn, ValidationError
from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

base_path = Path(__file__).parent.parent


class Config(BaseSettings):
    """A general configuration setup to read either .env or environment keys."""

    # Bot deploy config
    PORT: int = 8080
    HOSTNAME: str = "0.0.0.0"  # noqa: S104

    API_ID: int
    API_HASH: str
    BOT_TOKEN: str
    MONGO_DB_URL: MongoDsn

    # Bot main config
    BACKUP_CHANNEL: int
    ROOT_ADMINS_ID: list[int]
    FORCE_SUB_CHANNELS: list[int]

    model_config = SettingsConfigDict(
        env_file=f"{base_path}/.env",
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
