import logging

from universal_bot.application.dto.common.policy import Policy
from universal_bot.application.exception.common import AccessRevokedError
from universal_bot.application.port.persistence.repository.access_grant.reader import (
    IAccessGrantReader,
)
from universal_bot.application.port.persistence.repository.administrator.reader import (
    IAdministratorReader,
)
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.entity.administrator import Administrator
from universal_bot.domain.exception.access import AdminConfigurationMismatchError
from universal_bot.domain.value_object.user.id import TelegramUserId


class AccessPolicy:
    def __init__(
        self,
        *,
        access_grant_reader: IAccessGrantReader,
        administrator_reader: IAdministratorReader,
        policy: Policy,
    ) -> None:
        self._access_grant_reader = access_grant_reader
        self._administrator_reader = administrator_reader
        self._configured_user_id = TelegramUserId(policy.admin_id)

    async def administrator(self) -> Administrator:
        administrator = await self._administrator_reader.get()
        ensure(
            administrator,
            AdminConfigurationMismatchError,
            "Администратор ещё не зарегистрирован",
        )
        administrator.require_configuration(self._configured_user_id)
        return administrator

    async def allowed(self, *, user_id: int) -> bool:
        administrator = await self.administrator()
        actor = TelegramUserId(user_id)
        return (
            administrator.is_administrator(actor)
            or await self._access_grant_reader.find_by_id(key=actor) is not None
        )

    async def require_access(self, *, user_id: int) -> None:
        ensure(
            await self.allowed(user_id=user_id),
            AccessRevokedError,
            "Доступ пока не открыт",
        )

    async def require_admin(self, *, actor_id: int) -> None:
        administrator = await self.administrator()
        if not administrator.is_administrator(TelegramUserId(actor_id)):
            logging.getLogger(__name__).warning(
                "Administrative access denied",
                extra={"event": "admin_access_denied", "actor_id": actor_id},
            )
        administrator.require_administrator(TelegramUserId(actor_id))
