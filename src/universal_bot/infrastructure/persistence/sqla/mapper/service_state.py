from sqlalchemy.orm import composite

from universal_bot.domain.entity.service_state import ServiceState
from universal_bot.domain.value_object.service_state.key import ServiceStateKey
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.service_state import (
    service_state_table,
)


def map_service_state_table() -> None:
    mapping_registry.map_imperatively(
        ServiceState,
        service_state_table,
        properties={
            "_id": composite(ServiceStateKey, service_state_table.c.key),
            "value": service_state_table.c.value,
        },
        column_prefix="_raw_",
    )
