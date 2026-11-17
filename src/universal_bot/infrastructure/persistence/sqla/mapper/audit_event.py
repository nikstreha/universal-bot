from sqlalchemy.orm import composite

from universal_bot.domain.entity.audit_event import AuditEvent
from universal_bot.domain.enum.access.action import AccessAction
from universal_bot.domain.value_object.audit_event.id import AuditEventId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.audit_event import (
    audit_event_table,
)
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_audit_event_table() -> None:
    audit_event_table.c.action.type = EnumStringType(AccessAction)
    mapping_registry.map_imperatively(
        AuditEvent,
        audit_event_table,
        properties={
            "_id": composite(AuditEventId, audit_event_table.c.id),
            "actor_id": composite(TelegramUserId, audit_event_table.c.actor_id),
            "target_id": composite(TelegramUserId, audit_event_table.c.target_id),
            "action": audit_event_table.c.action,
            "created_at": composite(Timestamp, audit_event_table.c.created_at),
        },
        column_prefix="_raw_",
    )
