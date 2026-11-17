from universal_bot.domain.entity.common import Entity
from universal_bot.domain.enum.access.source import AccessSource
from universal_bot.domain.enum.access_request.status import AccessRequestStatus
from universal_bot.domain.exception.access_request import (
    AccessRequestAlreadyDecidedError,
)
from universal_bot.domain.value_object.access_request.id import AccessRequestId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId


class AccessRequest(Entity[AccessRequestId]):
    _id: AccessRequestId
    user_id: TelegramUserId
    source: AccessSource
    created_at: Timestamp
    status: AccessRequestStatus
    decided_at: Timestamp | None
    decided_by: TelegramUserId | None

    def __init__(
        self,
        *,
        id_: AccessRequestId,
        user_id: TelegramUserId,
        source: AccessSource,
        created_at: Timestamp,
        status: AccessRequestStatus = AccessRequestStatus.PENDING,
        decided_at: Timestamp | None = None,
        decided_by: TelegramUserId | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self.user_id = user_id
        self.source = source
        self.created_at = created_at
        self._status = status
        self.decided_at = decided_at
        self.decided_by = decided_by

    @property
    def status(self) -> AccessRequestStatus:
        return self._status

    def decide(self, approved: bool, actor: TelegramUserId, at: Timestamp) -> None:
        if self.status is not AccessRequestStatus.PENDING:
            raise AccessRequestAlreadyDecidedError()
        self._status = (
            AccessRequestStatus.APPROVED if approved else AccessRequestStatus.REJECTED
        )
        self.decided_at, self.decided_by = (at, actor)

    def mark_access_granted(self, actor: TelegramUserId, at: Timestamp) -> None:
        self._status = AccessRequestStatus.APPROVED
        self.decided_at, self.decided_by = (at, actor)
