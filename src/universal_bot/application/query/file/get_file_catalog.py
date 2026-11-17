from universal_bot.application.dto.common.pagination import PaginatedResponse
from universal_bot.application.dto.file.filter import FileFilterDTO
from universal_bot.application.port.persistence.repository.stored_file.reader import (
    IStoredFileReader,
)
from universal_bot.application.query_model.stored_file import StoredFileQueryModel
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.common import InvalidRequestError, NotFoundError
from universal_bot.domain.value_object.stored_file.id import StoredFileId
from universal_bot.domain.value_object.user.id import TelegramUserId


class GetFileCatalogInteractor:
    def __init__(
        self, *, access_policy: AccessPolicy, file_reader: IStoredFileReader
    ) -> None:
        self._access_policy = access_policy
        self._file_reader = file_reader

    async def __call__(
        self,
        *,
        user_id: int,
        state: str = "active",
        collection: str = "",
        kind: str = "",
        q: str = "",
        date_from: str = "",
        date_to: str = "",
        cursor: str = "",
        limit: int = 50,
    ) -> PaginatedResponse[StoredFileQueryModel]:
        await self._access_policy.require_access(user_id=user_id)
        ensure(1 <= limit <= 100, InvalidRequestError, "Неверный размер страницы")
        filters = FileFilterDTO(state, collection, kind, q, date_from, date_to)
        anchor = None
        if cursor:
            row = await self._file_reader.find_by_id(key=StoredFileId(cursor))
            ensure(
                row and row.owner_id == user_id and (row.state == state),
                NotFoundError,
                "Страница не найдена",
            )
            anchor = (row.storage_date, row.created_at, row.id)
        rows = await self._file_reader.get_catalog(
            owner_id=TelegramUserId(user_id),
            filters=filters,
            cursor=anchor,
            limit=limit + 1,
        )
        return PaginatedResponse(
            items=rows[:limit],
            next_cursor=rows[limit - 1].id if len(rows) > limit else None,
        )
