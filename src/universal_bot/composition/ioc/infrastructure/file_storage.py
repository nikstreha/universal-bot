from dishka import Provider, Scope, provide

from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.composition.configuration.file_storage_configuration import (
    FileStorageConfiguration,
)
from universal_bot.infrastructure.persistence.file_storage.minio import MinioStorage


class FileStorageProvider(Provider):
    @provide(scope=Scope.APP)
    def storage(self, config: FileStorageConfiguration) -> IObjectStorage:
        return MinioStorage(
            config.endpoint,
            config.user,
            config.password,
            config.bucket,
            config.secure,
            config.disk_path,
            config.require_mount,
            config.min_free_bytes,
        )
