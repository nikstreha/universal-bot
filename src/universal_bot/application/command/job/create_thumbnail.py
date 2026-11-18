from universal_bot.application.port.clock import IClock
from universal_bot.application.port.media.thumbnailer import IThumbnailer
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.application.port.persistence.repository.stored_file.writer import (
    IStoredFileWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.job import Job
from universal_bot.domain.exception.job import LeaseLostError
from universal_bot.domain.value_object.file.object_key import ObjectKey
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class CreateThumbnailInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        storage: IObjectStorage,
        stored_file_writer: IStoredFileWriter,
        thumbnailer: IThumbnailer,
        uow: IUnitOfWork,
        clock: IClock,
        job_writer: IJobWriter,
    ) -> None:
        self._access_policy = access_policy
        self._storage = storage
        self._stored_file_writer = stored_file_writer
        self._thumbnailer = thumbnailer
        self._uow = uow
        self._clock = clock
        self._job_writer = job_writer

    async def __call__(self, *, job: Job) -> None:
        async with self._uow:
            current_job = await self._job_writer.find_by_id(key=job.id_)
            ensure(current_job, LeaseLostError, "Задача не найдена")
            current_job.validate_lease(job.generation, Timestamp(self._clock.now()))
            file = await self._stored_file_writer.find_by_id(
                key=StoredFileId(str(job.resource_id.value))
            )
            if (
                not file
                or file.state != "active"
                or (not await self._access_policy.allowed(user_id=file.owner_id.value))
            ):
                return
        key = file.thumbnail_target(job.generation).value
        await self._thumbnailer.create(
            file.object_key.value,
            key,
            file.media_kind,
            file.size_bytes.value,
        )
        published = False
        async with self._uow:
            current_job = await self._job_writer.find_by_id(key=job.id_)
            ensure(current_job, LeaseLostError, "Задача не найдена")
            current_job.validate_lease(job.generation, Timestamp(self._clock.now()))
            fresh = await self._stored_file_writer.find_by_id(key=file.id_)
            if (
                fresh
                and fresh.state == "active"
                and await self._access_policy.allowed(user_id=fresh.owner_id.value)
            ):
                fresh.publish_thumbnail(ObjectKey(key))
                published = True
        if not published:
            await self._storage.delete(key)
