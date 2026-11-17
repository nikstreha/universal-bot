from universal_bot.domain.entity.common import Entity
from universal_bot.domain.enum.admin_dialog.action import AdminDialogAction
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class AccessDialog(Entity[TelegramUserId]):
    _identity_field = "admin_id"
    admin_id: TelegramUserId
    action: AdminDialogAction
    expires_at: Timestamp
    payload: str

    def __init__(
        self,
        *,
        admin_id: TelegramUserId,
        action: AdminDialogAction,
        expires_at: Timestamp,
        payload: str = "{}",
    ) -> None:
        super().__init__(id_=admin_id)
        self.action = action
        self.expires_at = expires_at
        self.payload = payload

    @property
    def admin_id(self) -> TelegramUserId:
        return self.id_

    def update(self, action: AdminDialogAction, payload: str, at: Timestamp) -> None:
        self.action, self.payload, self.expires_at = (action, payload, at.after(900))

    def is_expired(self, at: Timestamp) -> bool:
        return self.expires_at.value <= at.value
