from sqlalchemy.orm import composite

from universal_bot.domain.entity.admin_notification import AdminNotification
from universal_bot.domain.enum.access.source import AccessSource
from universal_bot.domain.enum.notification.outcome import LoginOutcome
from universal_bot.domain.value_object.notification.event_key import EventKey
from universal_bot.domain.value_object.notification.id import NotificationId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.admin_notification import (
    admin_notification_table,
)
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_admin_notification_table() -> None:
    admin_notification_table.c.source.type = EnumStringType(AccessSource)
    admin_notification_table.c.outcome.type = EnumStringType(LoginOutcome)
    mapping_registry.map_imperatively(
        AdminNotification,
        admin_notification_table,
        properties={
            "_id": composite(NotificationId, admin_notification_table.c.id),
            "event_key": composite(EventKey, admin_notification_table.c.event_key),
            "user_id": composite(TelegramUserId, admin_notification_table.c.user_id),
            "source": admin_notification_table.c.source,
            "outcome": admin_notification_table.c.outcome,
            "created_at": composite(Timestamp, admin_notification_table.c.created_at),
            "read_at": composite(
                Timestamp.from_raw, admin_notification_table.c.read_at
            ),
        },
        column_prefix="_raw_",
    )
