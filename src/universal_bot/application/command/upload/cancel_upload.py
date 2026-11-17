from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.upload.writer import (
    IUploadWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.upload.id import UploadId
from universal_bot.domain.value_object.user.id import TelegramUserId


class CancelUploadInteractor:
    def __init__(
        self,
        *,
        uow: IUnitOfWork,
        access_policy: AccessPolicy,
        clock: IClock,
        upload_writer: IUploadWriter,
    ) -> None:
        self._uow = uow
        self._access_policy = access_policy
        self._clock = clock
        self._upload_writer = upload_writer

    async def __call__(self, *, user_id: int, upload_id: str) -> None:
        async with self._uow:
            await self._access_policy.require_access(user_id=user_id)
            upload = await self._upload_writer.find_by_id(key=UploadId(upload_id))
            ensure(upload, NotFoundError, "Загрузка не найдена")
            upload.require_owner(TelegramUserId(user_id))
            upload.expire(Timestamp(self._clock.now()))
            upload.cancel()
