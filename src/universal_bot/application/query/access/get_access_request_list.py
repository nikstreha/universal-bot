from universal_bot.application.port.persistence.repository.access_request.reader import (
    IAccessRequestReader,
)
from universal_bot.application.port.persistence.repository.user.reader import (
    IUserReader,
)
from universal_bot.application.query_model.access_request import AccessRequestQueryModel
from universal_bot.application.query_model.user import UserQueryModel
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.enum.access_request.status import AccessRequestStatus
from universal_bot.domain.value_object.user.id import TelegramUserId


class GetAccessRequestListInteractor:
    def __init__(
        self,
        *,
        access_policy: AccessPolicy,
        access_request_reader: IAccessRequestReader,
        user_reader: IUserReader,
    ) -> None:
        self._access_policy = access_policy
        self._access_request_reader = access_request_reader
        self._user_reader = user_reader

    async def __call__(
        self, *, actor_id: int, status: str = "pending", offset: int = 0
    ) -> list[tuple[AccessRequestQueryModel, UserQueryModel]]:
        await self._access_policy.require_admin(actor_id=actor_id)
        rows = await self._access_request_reader.get_page_by_status(
            status=AccessRequestStatus(status), limit=offset + 10
        )
        return [
            (row, await self._user_reader.find_by_id(key=TelegramUserId(row.user_id)))
            for row in rows[offset:]
        ]
