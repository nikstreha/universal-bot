from dataclasses import replace

from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.upload.reader import (
    IUploadReader,
)
from universal_bot.application.port.persistence.repository.upload_part.reader import (
    IUploadPartReader,
)
from universal_bot.application.query_model.upload import UploadQueryModel
from universal_bot.application.query_model.upload_part import UploadPartQueryModel
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.value_object.upload.id import UploadId


class GetUploadInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        upload_reader: IUploadReader,
        part_reader: IUploadPartReader,
        clock: IClock,
    ) -> None:
        self._access_policy = access_policy
        self._upload_reader = upload_reader
        self._part_reader = part_reader
        self._clock = clock

    async def __call__(
        self, *, user_id: int, upload_id: str
    ) -> tuple[UploadQueryModel, list[UploadPartQueryModel]]:
        await self._access_policy.require_access(user_id=user_id)
        row = await self._upload_reader.find_by_id(key=UploadId(upload_id))
        ensure(row and row.owner_id == user_id, NotFoundError, "Загрузка не найдена")
        if row.state == "receiving" and row.expires_at <= self._clock.now():
            row = replace(row, state="expired")
        parts = await self._part_reader.list_by_upload_id(upload_id=UploadId(upload_id))
        return (row, parts)
