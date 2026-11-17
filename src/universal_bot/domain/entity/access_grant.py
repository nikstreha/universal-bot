from universal_bot.domain.entity.common import Entity
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class AccessGrant(Entity[TelegramUserId]):
    _identity_field = "user_id"
    user_id: TelegramUserId
    added_at: Timestamp
    added_by: TelegramUserId

    def __init__(
        self, *, user_id: TelegramUserId, added_at: Timestamp, added_by: TelegramUserId
    ) -> None:
        super().__init__(id_=user_id)
        self.added_at = added_at
        self.added_by = added_by

    @property
    def user_id(self) -> TelegramUserId:
        return self.id_
