from universal_bot.application.dto.common.pagination import PaginatedResponse
from universal_bot.application.dto.file.filter import FileFilterDTO
from universal_bot.application.port.persistence.repository.stored_file.reader import (
    IStoredFileReader,
)
from universal_bot.application.query_model.file_date_group import (
    FileDateGroupQueryModel,
)
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.common import InvalidRequestError
from universal_bot.domain.value_object.user.id import TelegramUserId


class GetFileDateListInteractor:
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
        cursor: str = "",
        limit: int = 31,
    ) -> PaginatedResponse[FileDateGroupQueryModel]:
        await self._access_policy.require_access(user_id=user_id)
        ensure(1 <= limit <= 100, InvalidRequestError, "Неверный размер страницы")
        filters = FileFilterDTO(state, collection, kind, q, date_to=cursor)
        rows = await self._file_reader.get_date_groups(
            owner_id=TelegramUserId(user_id),
            filters=filters,
            before_date=cursor,
            limit=limit + 1,
        )
        return PaginatedResponse(
            items=rows[:limit],
            next_cursor=rows[limit - 1].storage_date if len(rows) > limit else None,
        )
