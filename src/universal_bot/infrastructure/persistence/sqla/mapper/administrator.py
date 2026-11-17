from sqlalchemy.orm import composite

from universal_bot.domain.entity.administrator import Administrator
from universal_bot.domain.value_object.administrator.id import AdministratorId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.administrator import (
    administrator_table,
)


def map_administrator_table() -> None:
    mapping_registry.map_imperatively(
        Administrator,
        administrator_table,
        properties={
            "_id": composite(AdministratorId, administrator_table.c.id),
            "_user_id": composite(TelegramUserId, administrator_table.c.user_id),
            "created_at": composite(Timestamp, administrator_table.c.created_at),
        },
        column_prefix="_raw_",
    )
