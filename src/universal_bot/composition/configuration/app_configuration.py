from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from universal_bot.composition.configuration.asr_configuration import AsrConfiguration
from universal_bot.composition.configuration.file_storage_configuration import (
    FileStorageConfiguration,
)
from universal_bot.composition.configuration.media_configuration import (
    MediaConfiguration,
)
from universal_bot.composition.configuration.persistence_configuration import (
    PersistenceConfiguration,
)
from universal_bot.composition.configuration.security_configuration import (
    SecurityConfiguration,
)
from universal_bot.composition.configuration.server_configuration import (
    ServerConfiguration,
)
from universal_bot.composition.configuration.storage_configuration import (
    StorageConfiguration,
)
from universal_bot.composition.configuration.telegram_configuration import (
    TelegramConfiguration,
)


class AppConfiguration(BaseSettings):
    persistence: PersistenceConfiguration = Field(
        default_factory=PersistenceConfiguration
    )
    security: SecurityConfiguration
    server: ServerConfiguration = Field(default_factory=ServerConfiguration)
    storage: StorageConfiguration = Field(default_factory=StorageConfiguration)
    file_storage: FileStorageConfiguration = Field(
        default_factory=FileStorageConfiguration
    )
    telegram: TelegramConfiguration = Field(default_factory=TelegramConfiguration)
    asr: AsrConfiguration = Field(default_factory=AsrConfiguration)
    media: MediaConfiguration = Field(default_factory=MediaConfiguration)

    model_config = SettingsConfigDict(
        env_file=Path.cwd() / ".env",
        env_file_encoding="utf-8",
        env_prefix="APP__",
        env_nested_delimiter="__",
        extra="ignore",
    )
