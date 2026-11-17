from sqlalchemy.orm import composite

from universal_bot.domain.entity.user import User
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.domain.value_object.user.name import UserName
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.user import user_table


def map_user_table() -> None:
    mapping_registry.map_imperatively(
        User,
        user_table,
        properties={
            "_id": composite(TelegramUserId, user_table.c.id),
            "name": composite(UserName, user_table.c.name),
            "created_at": composite(Timestamp, user_table.c.created_at),
            "last_seen_at": composite(Timestamp, user_table.c.last_seen_at),
        },
        column_prefix="_raw_",
    )
