import asyncio
import hashlib
import os
import shutil
from contextlib import suppress
from pathlib import Path
from typing import Any

from universal_bot.application.exception.infrastructure.file_storage import (
    StorageFullError,
    StorageUnavailableError,
)
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
    IObjectStream,
)
from universal_bot.domain.common.guard import ensure
from universal_bot.infrastructure.persistence.file_storage.error import (
    storage_operation,
)


class S3ObjectStream(IObjectStream):
    def __init__(self, body: Any) -> None:
        self._body = body
        self._closed = False

    @storage_operation
    async def read(self, size: int = -1) -> bytes:
        return await self._body.read(size)

    async def close(self) -> None:
        if not self._closed:
            self._closed = True
            self._body.close()


class S3Storage(IObjectStorage):
    """Async S3 with distinct buckets for originals and temporary upload parts.

    Garage authorizes by bucket rather than by key prefix. Keeping staging in its
    own bucket lets the API upload parts without being able to delete originals.
    Buckets and keys are provisioned separately; runtime never creates buckets.
    """

    def __init__(
        self,
        client: Any,
        bucket: str,
        staging_bucket: str,
        disk_path: Path | None = None,
        require_mount: bool = False,
        min_free_bytes: int = 1024**3,
    ) -> None:
        self._client, self._bucket, self._staging_bucket = (
            client,
            bucket,
            staging_bucket,
        )
        self._disk_path = disk_path
        self._require_mount, self._min_free_bytes = require_mount, min_free_bytes

    def _bucket_for(self, key: str) -> str:
        return self._staging_bucket if key.startswith("staging/") else self._bucket

    def _guard(self, needed: int, check_space: bool = True) -> None:
        path = self._disk_path
        if path is not None:
            ensure(path.exists(), StorageUnavailableError, "Диск недоступен")
            ensure(
                not self._require_mount or os.path.ismount(path),
                StorageUnavailableError,
                "Диск не смонтирован",
            )
            if check_space:
                ensure(
                    shutil.disk_usage(path).free > needed + self._min_free_bytes,
                    StorageFullError,
                    "Недостаточно места на сервере",
                )

    @storage_operation
    async def guard(self, needed: int = 0) -> None:
        await asyncio.to_thread(self._guard, needed)

    @storage_operation
    async def ready(self) -> None:
        await self.guard()
        for bucket in dict.fromkeys((self._bucket, self._staging_bucket)):
            await self._client.head_bucket(Bucket=bucket)

    @storage_operation
    async def put(
        self, key: str, data: bytes, mime: str = "application/octet-stream"
    ) -> None:
        await self.guard(len(data))
        await self._client.put_object(
            Bucket=self._bucket_for(key), Key=key, Body=data, ContentType=mime
        )

    @storage_operation
    async def compose(self, key: str, parts: list[str]) -> None:
        if not parts:
            await self.put(key, b"")
            return
        bucket = self._bucket_for(key)
        if len(parts) == 1:
            await self._client.copy_object(
                Bucket=bucket,
                Key=key,
                CopySource={"Bucket": self._bucket_for(parts[0]), "Key": parts[0]},
            )
            return
        upload = await self._client.create_multipart_upload(Bucket=bucket, Key=key)
        upload_id = upload["UploadId"]
        completed = []
        try:
            for number, source in enumerate(parts, 1):
                size = await self.size(source)
                if size < 5 * 1024**2:
                    # Garage rejects UploadPartCopy below 5 MiB even for the last
                    # part. Regular UploadPart supports a short final part.
                    ensure(
                        number == len(parts),
                        StorageUnavailableError,
                        "Промежуточная часть загрузки слишком мала",
                    )
                    stream = await self.read(source)
                    data = bytearray()
                    try:
                        while chunk := await stream.read(
                            min(1024**2, 5 * 1024**2 + 1 - len(data))
                        ):
                            data.extend(chunk)
                            ensure(
                                len(data) <= size,
                                StorageUnavailableError,
                                "Часть загрузки изменилась",
                            )
                    finally:
                        await stream.close()
                    ensure(
                        len(data) == size,
                        StorageUnavailableError,
                        "Часть загрузки неполная",
                    )
                    result = await self._client.upload_part(
                        Bucket=bucket,
                        Key=key,
                        UploadId=upload_id,
                        PartNumber=number,
                        Body=bytes(data),
                    )
                    etag = result["ETag"]
                else:
                    result = await self._client.upload_part_copy(
                        Bucket=bucket,
                        Key=key,
                        UploadId=upload_id,
                        PartNumber=number,
                        CopySource={"Bucket": self._bucket_for(source), "Key": source},
                    )
                    etag = result["CopyPartResult"]["ETag"]
                completed.append({"ETag": etag, "PartNumber": number})
            await self._client.complete_multipart_upload(
                Bucket=bucket,
                Key=key,
                UploadId=upload_id,
                MultipartUpload={"Parts": completed},
            )
        except BaseException:
            with suppress(Exception):
                await self._client.abort_multipart_upload(
                    Bucket=bucket, Key=key, UploadId=upload_id
                )
            raise

    @storage_operation
    async def read(self, key: str, offset: int = 0, length: int = 0) -> IObjectStream:
        if offset < 0 or length < 0:
            raise ValueError("Range must be non-negative")
        arguments = {"Bucket": self._bucket_for(key), "Key": key}
        if length:
            arguments["Range"] = f"bytes={offset}-{offset + length - 1}"
        elif offset:
            arguments["Range"] = f"bytes={offset}-"
        result = await self._client.get_object(**arguments)
        return S3ObjectStream(result["Body"])

    @storage_operation
    async def size(self, key: str) -> int:
        result = await self._client.head_object(Bucket=self._bucket_for(key), Key=key)
        return result["ContentLength"]

    @storage_operation
    async def delete(self, key: str) -> None:
        # Cleanup must remain possible below the upload free-space watermark.
        await asyncio.to_thread(self._guard, 0, False)
        await self._client.delete_object(Bucket=self._bucket_for(key), Key=key)

    @storage_operation
    async def download(self, key: str, path: str) -> None:
        await self.guard()
        source = await self.read(key)
        try:
            with Path(path).open("wb") as output:
                while chunk := await source.read(1024 * 1024):
                    await asyncio.to_thread(output.write, chunk)
        finally:
            await source.close()

    async def close(self, response: IObjectStream) -> None:
        await response.close()

    @storage_operation
    async def inspect(self, key: str) -> tuple[int, str, bytes]:
        source = await self.read(key)
        size, header, digest = 0, b"", hashlib.sha256()
        try:
            while chunk := await source.read(1024 * 1024):
                if len(header) < 8192:
                    header += chunk[: 8192 - len(header)]
                size += len(chunk)
                digest.update(chunk)
        finally:
            await source.close()
        return size, digest.hexdigest(), header
