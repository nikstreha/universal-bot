from universal_bot.application.dto.common.policy import Policy
from universal_bot.application.port.persistence.repository.user.reader import (
    IUserReader,
)
from universal_bot.application.query_model.user import AdminUserQueryModel
from universal_bot.application.service.access.access_policy import AccessPolicy
from universal_bot.domain.value_object.user.id import TelegramUserId


class GetUserListInteractor:
    def __init__(
        self, *, access_policy: AccessPolicy, user_reader: IUserReader, policy: Policy
    ) -> None:
        self._access_policy = access_policy
        self._user_reader = user_reader
        self._policy = policy

    async def __call__(self, *, actor_id: int) -> list[AdminUserQueryModel]:
        await self._access_policy.require_admin(actor_id=actor_id)
        return await self._user_reader.get_whitelisted_with_usage(
            admin_id=TelegramUserId(self._policy.admin_id)
        )
