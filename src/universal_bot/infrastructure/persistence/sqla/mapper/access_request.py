from sqlalchemy.orm import composite

from universal_bot.domain.entity.access_request import AccessRequest
from universal_bot.domain.enum.access.source import AccessSource
from universal_bot.domain.enum.access_request.status import AccessRequestStatus
from universal_bot.domain.value_object.access_request.id import AccessRequestId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.access_request import (
    access_request_table,
)
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_access_request_table() -> None:
    access_request_table.c.source.type = EnumStringType(AccessSource)
    access_request_table.c.status.type = EnumStringType(AccessRequestStatus)
    mapping_registry.map_imperatively(
        AccessRequest,
        access_request_table,
        properties={
            "_id": composite(AccessRequestId, access_request_table.c.id),
            "user_id": composite(TelegramUserId, access_request_table.c.user_id),
            "source": access_request_table.c.source,
            "created_at": composite(Timestamp, access_request_table.c.created_at),
            "_status": access_request_table.c.status,
            "decided_at": composite(
                Timestamp.from_raw, access_request_table.c.decided_at
            ),
            "decided_by": composite(
                TelegramUserId.from_raw, access_request_table.c.decided_by
            ),
        },
        column_prefix="_raw_",
    )
