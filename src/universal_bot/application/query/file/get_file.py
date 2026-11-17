from universal_bot.application.port.persistence.repository.stored_file.reader import (
    IStoredFileReader,
)
from universal_bot.application.query_model.stored_file import StoredFileQueryModel
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.value_object.stored_file.id import StoredFileId


class GetFileInteractor:
    def __init__(
        self, *, access_policy: AccessPolicy, file_reader: IStoredFileReader
    ) -> None:
        self._access_policy = access_policy
        self._file_reader = file_reader

    async def __call__(self, *, user_id: int, file_id: str) -> StoredFileQueryModel:
        await self._access_policy.require_access(user_id=user_id)
        row = await self._file_reader.find_by_id(key=StoredFileId(file_id))
        ensure(
            row and row.owner_id == user_id and (row.state != "purging"),
            NotFoundError,
            "Файл не найден",
        )
        return row
