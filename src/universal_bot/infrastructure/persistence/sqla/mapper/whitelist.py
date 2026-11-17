from sqlalchemy.orm import composite

from universal_bot.domain.entity.access_grant import AccessGrant
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.whitelist import (
    whitelist_table,
)


def map_whitelist_table() -> None:
    mapping_registry.map_imperatively(
        AccessGrant,
        whitelist_table,
        properties={
            "_id": composite(TelegramUserId, whitelist_table.c.user_id),
            "added_at": composite(Timestamp, whitelist_table.c.added_at),
            "added_by": composite(TelegramUserId, whitelist_table.c.added_by),
        },
        column_prefix="_raw_",
    )
