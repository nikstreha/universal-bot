from sqlalchemy.orm import composite

from universal_bot.domain.entity.telegram_update import TelegramUpdate
from universal_bot.domain.enum.telegram_update.state import TelegramUpdateState
from universal_bot.domain.value_object.messaging.update_id import TelegramUpdateId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.telegram_update import (
    telegram_update_table,
)
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_telegram_update_table() -> None:
    telegram_update_table.c.state.type = EnumStringType(TelegramUpdateState)
    mapping_registry.map_imperatively(
        TelegramUpdate,
        telegram_update_table,
        properties={
            "_id": composite(TelegramUpdateId, telegram_update_table.c.id),
            "payload": telegram_update_table.c.payload,
            "created_at": composite(Timestamp, telegram_update_table.c.created_at),
            "_state": telegram_update_table.c.state,
        },
        column_prefix="_raw_",
    )
