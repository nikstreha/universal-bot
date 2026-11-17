from universal_bot.domain.entity.common import Entity
from universal_bot.domain.exception.access import (
    AdminConfigurationMismatchError,
    AdminRequiredError,
)
from universal_bot.domain.value_object.administrator.id import AdministratorId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class Administrator(Entity[AdministratorId]):
    user_id: TelegramUserId
    created_at: Timestamp

    def __init__(
        self,
        *,
        user_id: TelegramUserId,
        created_at: Timestamp,
        id_: AdministratorId = AdministratorId(),
    ) -> None:
        super().__init__(id_=id_)
        self._user_id = user_id
        self.created_at = created_at

    @property
    def user_id(self) -> TelegramUserId:
        return self._user_id

    def require_configuration(self, user_id: TelegramUserId) -> None:
        if self.user_id != user_id:
            raise AdminConfigurationMismatchError(
                "Администратор отличается от сохранённого владельца базы"
            )

    def is_administrator(self, user_id: TelegramUserId) -> bool:
        return self.user_id == user_id

    def require_administrator(self, user_id: TelegramUserId) -> None:
        if not self.is_administrator(user_id):
            raise AdminRequiredError("Недостаточно прав")
