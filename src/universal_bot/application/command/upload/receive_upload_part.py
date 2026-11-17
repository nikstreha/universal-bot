import asyncio

from universal_bot.application.dto.common.policy import Policy
from universal_bot.application.exception.common import PartConflictError
from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.application.port.persistence.repository.upload.writer import (
    IUploadWriter,
)
from universal_bot.application.port.persistence.repository.upload_part.writer import (
    IUploadPartWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.port.security.secrets import ISecrets
from universal_bot.application.query.upload.get_upload_part_size import (
    GetUploadPartSizeInteractor,
)
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.upload_part import UploadPart
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.exception.file import ChecksumMismatchError
from universal_bot.domain.value_object.file.object_key import ObjectKey
from universal_bot.domain.value_object.file.sha256 import SHA256Digest
from universal_bot.domain.value_object.file.size import FileSize
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.upload.part_id import UploadPartId
from universal_bot.domain.value_object.upload.part_index import PartIndex
from universal_bot.domain.value_object.user.id import TelegramUserId


class ReceiveUploadPartInteractor:
    def __init__(
        self,
        *,
        clock: IClock,
        get_upload_part_size: GetUploadPartSizeInteractor,
        policy: Policy,
        secrets: ISecrets,
        storage: IObjectStorage,
        uow: IUnitOfWork,
        upload_part_writer: IUploadPartWriter,
        access_policy: AccessPolicy,
        upload_writer: IUploadWriter,
    ) -> None:
        self._clock = clock
        self._get_upload_part_size = get_upload_part_size
        self._policy = policy
        self._secrets = secrets
        self._storage = storage
        self._uow = uow
        self._upload_part_writer = upload_part_writer
        self._access_policy = access_policy
        self._upload_writer = upload_writer

    async def __call__(
        self,
        *,
        user_id: int,
        upload_id: str,
        index: int,
        data: bytes,
        expected_hash: str,
    ) -> None:
        expected = await self._get_upload_part_size(
            user_id=user_id, upload_id=upload_id, index=index
        )
        ensure(
            len(data) == expected and self._secrets.hash(data) == expected_hash,
            ChecksumMismatchError,
            "Хеш части не совпадает",
        )
        key = f"staging/{upload_id}/{index}/{self._secrets.identity()}"
        await asyncio.to_thread(self._storage.put, key, data)
        published = False
        created = False
        try:
            async with self._uow:
                await self._access_policy.require_access(user_id=user_id)
                upload = await self._upload_writer.find_by_id(key=UploadId(upload_id))
                ensure(upload, NotFoundError, "Загрузка не найдена")
                upload.require_owner(TelegramUserId(user_id))
                upload.expire(Timestamp(self._clock.now()))
                upload.accept(Timestamp(self._clock.now()))
                existing = await self._upload_part_writer.find_by_id(
                    key=UploadPartId.from_raw((upload_id, index))
                )
                if existing:
                    ensure(
                        existing.sha256.value == expected_hash
                        and existing.size_bytes.value == expected,
                        PartConflictError,
                        "Часть содержит другие данные",
                    )
                else:
                    part = UploadPart(
                        upload_id=upload.id_,
                        part_index=PartIndex(index),
                        size_bytes=FileSize(expected),
                        sha256=SHA256Digest(expected_hash),
                        object_key=ObjectKey(key),
                    )
                    upload.record_part(
                        part,
                        Timestamp(self._clock.now()),
                        self._policy.upload_idle_seconds,
                    )
                    await self._upload_part_writer.add(entity=part)
                    created = True
            published = created
        finally:
            if not published:
                await asyncio.to_thread(self._storage.delete, key)
