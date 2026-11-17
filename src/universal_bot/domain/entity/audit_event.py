from universal_bot.domain.entity.common import Entity
from universal_bot.domain.enum.access.action import AccessAction
from universal_bot.domain.value_object.audit_event.id import AuditEventId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class AuditEvent(Entity[AuditEventId]):
    _id: AuditEventId
    actor_id: TelegramUserId
    target_id: TelegramUserId
    action: AccessAction
    created_at: Timestamp

    def __init__(
        self,
        *,
        id_: AuditEventId,
        actor_id: TelegramUserId,
        target_id: TelegramUserId,
        action: AccessAction,
        created_at: Timestamp,
    ) -> None:
        super().__init__(id_=id_)
        self.actor_id = actor_id
        self.target_id = target_id
        self.action = action
        self.created_at = created_at
