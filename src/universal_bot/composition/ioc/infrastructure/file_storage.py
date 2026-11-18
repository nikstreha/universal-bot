from collections.abc import AsyncIterator

import aioboto3
from botocore.config import Config
from dishka import Provider, Scope, provide

from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.composition.configuration.file_storage_configuration import (
    FileStorageConfiguration,
)
from universal_bot.infrastructure.persistence.file_storage.s3 import S3Storage


class FileStorageProvider(Provider):
    @provide(scope=Scope.APP)
    async def storage(
        self, config: FileStorageConfiguration
    ) -> AsyncIterator[IObjectStorage]:
        session = aioboto3.Session()
        async with session.client(
            "s3",
            endpoint_url=config.endpoint_url,
            region_name=config.region,
            aws_access_key_id=config.user,
            aws_secret_access_key=config.password,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path"},
                connect_timeout=5,
                read_timeout=60,
                max_pool_connections=32,
                retries={"mode": "standard", "max_attempts": 3},
                tcp_keepalive=True,
                request_checksum_calculation="when_required",
                response_checksum_validation="when_required",
            ),
        ) as client:
            yield S3Storage(
                client,
                config.bucket,
                config.staging_bucket,
                config.disk_path,
                config.require_mount,
                config.min_free_bytes,
            )
