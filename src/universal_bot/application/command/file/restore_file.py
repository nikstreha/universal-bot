from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.stored_file.writer import (
    IStoredFileWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.stored_file import StoredFile
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class RestoreFileInteractor:
    def __init__(
        self,
        *,
        clock: IClock,
        uow: IUnitOfWork,
        access_policy: AccessPolicy,
        stored_file_writer: IStoredFileWriter,
    ) -> None:
        self._clock = clock
        self._uow = uow
        self._access_policy = access_policy
        self._stored_file_writer = stored_file_writer

    async def __call__(self, *, user_id: int, file_id: str) -> StoredFile:
        async with self._uow:
            await self._access_policy.require_access(user_id=user_id)
            row = await self._stored_file_writer.find_by_id(key=StoredFileId(file_id))
            ensure(row, NotFoundError, "Файл не найден")
            row.require_owner(TelegramUserId(user_id))
            row.restore(Timestamp(self._clock.now()))
            return row
