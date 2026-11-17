import asyncio

from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.application.port.persistence.repository.stored_file.writer import (
    IStoredFileWriter,
)
from universal_bot.application.port.persistence.repository.upload.writer import (
    IUploadWriter,
)
from universal_bot.application.port.persistence.repository.upload_part.writer import (
    IUploadPartWriter,
)
from universal_bot.application.port.persistence.repository.verification.writer import (
    IVerificationWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.domain.enum.file.state import FileState
from universal_bot.domain.enum.upload.state import UploadState
from universal_bot.domain.value_object.time.timestamp import Timestamp


class MaintainStorageInteractor:
    def __init__(
        self,
        *,
        clock: IClock,
        storage: IObjectStorage,
        stored_file_writer: IStoredFileWriter,
        uow: IUnitOfWork,
        upload_part_writer: IUploadPartWriter,
        upload_writer: IUploadWriter,
        verification_writer: IVerificationWriter,
    ) -> None:
        self._clock = clock
        self._storage = storage
        self._stored_file_writer = stored_file_writer
        self._uow = uow
        self._upload_part_writer = upload_part_writer
        self._upload_writer = upload_writer
        self._verification_writer = verification_writer

    async def __call__(self) -> None:
        async with self._uow:
            expired = await self._upload_writer.list_by_state_expiring_before(
                state=UploadState.RECEIVING, expires_before=Timestamp(self._clock.now())
            )
            for upload in expired:
                upload.expire(Timestamp(self._clock.now()))
            purge = await self._stored_file_writer.list_due_for_purge(
                states=(FileState.TRASHED, FileState.PURGING),
                purge_before=Timestamp(self._clock.now()),
            )
            for file in purge:
                file.begin_purge(Timestamp(self._clock.now()))
        for file in purge:
            await asyncio.to_thread(self._storage.delete, file.object_key.value)
            if file.thumbnail_key is not None:
                await asyncio.to_thread(
                    self._storage.delete,
                    file.thumbnail_key.value,
                )
            async with self._uow:
                for check in await self._verification_writer.list_by_file_id(
                    file_id=file.id_
                ):
                    await self._verification_writer.delete(entity=check)
                current = await self._stored_file_writer.find_by_id(key=file.id_)
                if current and current.state is FileState.PURGING:
                    await self._stored_file_writer.delete(entity=current)
        async with self._uow:
            abandoned = await self._upload_writer.list_by_states(
                states=(
                    UploadState.EXPIRED,
                    UploadState.CANCELLED,
                    UploadState.FAILED,
                    UploadState.COMPLETED,
                )
            )
        for upload in abandoned:
            async with self._uow:
                parts = await self._upload_part_writer.list_by_upload_id(
                    upload_id=upload.id_
                )
            for part in parts:
                await asyncio.to_thread(self._storage.delete, part.object_key.value)
                async with self._uow:
                    fresh = await self._upload_part_writer.find_by_id(key=part.id_)
                    if fresh:
                        await self._upload_part_writer.delete(entity=fresh)
