from dishka import Provider, Scope, from_context, provide

from universal_bot.application.dto.common.policy import Policy
from universal_bot.composition.configuration.app_configuration import AppConfiguration
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
from universal_bot.composition.configuration.telegram_configuration import (
    TelegramConfiguration,
)
from universal_bot.presentation.http.telegram.configuration import WebhookConfiguration


class ConfigurationProvider(Provider):
    scope = Scope.APP
    configuration = from_context(provides=AppConfiguration)

    @provide
    def get_persistence_config(self, c: AppConfiguration) -> PersistenceConfiguration:
        return c.persistence

    @provide
    def get_file_storage_config(self, c: AppConfiguration) -> FileStorageConfiguration:
        return c.file_storage

    @provide
    def get_asr_config(self, c: AppConfiguration) -> AsrConfiguration:
        return c.asr

    @provide
    def get_telegram_config(self, c: AppConfiguration) -> TelegramConfiguration:
        return c.telegram

    @provide
    def get_media_config(self, c: AppConfiguration) -> MediaConfiguration:
        return c.media

    @provide
    def get_webhook_config(self, c: AppConfiguration) -> WebhookConfiguration:
        return WebhookConfiguration(
            secret=c.telegram.webhook_secret, enabled=c.telegram.mode == "webhook"
        )

    @provide
    def get_policy(self, c: AppConfiguration) -> Policy:
        return Policy(
            admin_id=c.security.admin_id,
            bot_username=c.telegram.username.lstrip("@"),
            archive_timezone=c.storage.archive_timezone,
            max_file_bytes=c.storage.max_file_bytes,
            part_bytes=c.storage.part_bytes,
            max_open_uploads=c.storage.max_open_uploads,
            upload_idle_seconds=c.storage.upload_idle_seconds,
            session_idle_seconds=c.security.session_idle_seconds,
            session_max_seconds=c.security.session_max_seconds,
            trash_retention_seconds=c.storage.trash_retention_days * 86400,
        )
