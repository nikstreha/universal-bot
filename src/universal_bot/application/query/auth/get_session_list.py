from universal_bot.application.port.persistence.repository.session.reader import (
    ISessionReader,
)
from universal_bot.application.query_model.session import SessionQueryModel
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.value_object.user.id import TelegramUserId


class GetSessionListInteractor:
    def __init__(
        self, *, access_policy: AccessPolicy, session_reader: ISessionReader
    ) -> None:
        self._access_policy = access_policy
        self._session_reader = session_reader

    async def __call__(self, *, user_id: int) -> list[SessionQueryModel]:
        await self._access_policy.require_access(user_id=user_id)
        return await self._session_reader.list_by_user_id(
            user_id=TelegramUserId(user_id), revoked_at=None
        )
