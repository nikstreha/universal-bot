import hashlib
import io
import os
import shutil
from pathlib import Path
from typing import BinaryIO, cast

import urllib3
from minio import Minio
from minio.commonconfig import ComposeSource
from minio.error import S3Error
from urllib3.response import HTTPResponse

from universal_bot.application.exception.infrastructure.file_storage import (
    StorageFullError,
    StoragePolicyUnsafeError,
    StorageUnavailableError,
)
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.domain.common.guard import ensure
from universal_bot.infrastructure.persistence.file_storage.error import (
    storage_operation,
)


class MinioStorage(IObjectStorage):
    def __init__(
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        bucket: str,
        secure: bool = False,
        disk_path: Path | None = None,
        require_mount: bool = False,
        min_free_bytes: int = 1024**3,
    ) -> None:
        self._disk_path, self._require_mount, self._min_free_bytes = (
            disk_path,
            require_mount,
            min_free_bytes,
        )
        self._client = Minio(
            endpoint,
            access_key=access_key,
            secret_key=secret_key,
            secure=secure,
            http_client=urllib3.PoolManager(
                timeout=urllib3.Timeout(connect=5, read=60),
                retries=urllib3.Retry(total=2, backoff_factor=0.3),
            ),
        )
        self._bucket = bucket

    @storage_operation
    def guard(self, needed: int = 0) -> None:
        path = self._disk_path
        if path:
            ensure(path.exists(), StorageUnavailableError, "Диск недоступен")
            ensure(
                not self._require_mount or os.path.ismount(path),
                StorageUnavailableError,
                "Диск не смонтирован",
            )
            ensure(
                shutil.disk_usage(path).free > needed + self._min_free_bytes,
                StorageFullError,
                "Недостаточно места на сервере",
            )

    @storage_operation
    def ready(self) -> None:
        self.guard()
        if not self._client.bucket_exists(self._bucket):
            self._client.make_bucket(self._bucket)
        try:
            policy = self._client.get_bucket_policy(self._bucket)
        except S3Error as exc:
            if exc.code != "NoSuchBucketPolicy":
                raise
        else:
            ensure(
                not policy,
                StoragePolicyUnsafeError,
                "Bucket должен быть приватным, без публичной bucket policy",
            )

    @storage_operation
    def put(
        self, key: str, data: bytes, mime: str = "application/octet-stream"
    ) -> None:
        self.guard(len(data))
        self._client.put_object(
            self._bucket, key, io.BytesIO(data), len(data), content_type=mime
        )

    @storage_operation
    def compose(self, key: str, parts: list[str]) -> None:
        if not parts:
            self.put(key, b"")
        else:
            self._client.compose_object(
                self._bucket, key, [ComposeSource(self._bucket, part) for part in parts]
            )

    @storage_operation
    def read(self, key: str, offset: int = 0, length: int = 0) -> BinaryIO:
        return cast(
            BinaryIO,
            self._client.get_object(self._bucket, key, offset=offset, length=length),
        )

    @storage_operation
    def delete(self, key: str) -> None:
        self.guard()
        self._client.remove_object(self._bucket, key)

    @storage_operation
    def size(self, key: str) -> int:
        return self._client.stat_object(self._bucket, key).size

    @storage_operation
    def download(self, key: str, path: str) -> None:
        self.guard()
        self._client.fget_object(self._bucket, key, str(path))

    def close(self, response: BinaryIO) -> None:
        stream = cast(HTTPResponse, response)
        stream.close()
        stream.release_conn()

    @storage_operation
    def inspect(self, key: str) -> tuple[int, str, bytes]:
        source = self.read(key)
        size, header, digest = 0, b"", hashlib.sha256()
        try:
            while chunk := source.read(1024 * 1024):
                if len(header) < 8192:
                    header += chunk[: 8192 - len(header)]
                size += len(chunk)
                digest.update(chunk)
        finally:
            self.close(source)
        return size, digest.hexdigest(), header
