from sqlalchemy.orm import composite

from universal_bot.domain.entity.rate_limit import RateLimit
from universal_bot.domain.value_object.rate_limit.key import RateLimitKey
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.rate_limit import (
    rate_limit_table,
)


def map_rate_limit_table() -> None:
    mapping_registry.map_imperatively(
        RateLimit,
        rate_limit_table,
        properties={
            "_id": composite(RateLimitKey, rate_limit_table.c.key),
            "window_start": composite(Timestamp, rate_limit_table.c.window_start),
            "count": rate_limit_table.c.count,
        },
        column_prefix="_raw_",
    )
