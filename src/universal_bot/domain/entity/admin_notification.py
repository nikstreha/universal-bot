from universal_bot.domain.entity.common import Entity
from universal_bot.domain.enum.access.source import AccessSource
from universal_bot.domain.enum.notification.outcome import LoginOutcome
from universal_bot.domain.value_object.notification.event_key import EventKey
from universal_bot.domain.value_object.notification.id import NotificationId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class AdminNotification(Entity[NotificationId]):
    _id: NotificationId
    event_key: EventKey
    user_id: TelegramUserId
    source: AccessSource
    outcome: LoginOutcome
    created_at: Timestamp
    read_at: Timestamp | None

    def __init__(
        self,
        *,
        id_: NotificationId,
        event_key: EventKey,
        user_id: TelegramUserId,
        source: AccessSource,
        outcome: LoginOutcome,
        created_at: Timestamp,
        read_at: Timestamp | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.event_key = event_key
        self.user_id = user_id
        self.source = source
        self.outcome = outcome
        self.created_at = created_at
        self.read_at = read_at

    def mark_read(self, at: Timestamp) -> None:
        if self.read_at is None:
            self.read_at = at
