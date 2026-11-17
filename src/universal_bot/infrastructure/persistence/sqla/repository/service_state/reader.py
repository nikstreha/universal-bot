from sqlalchemy import select

from universal_bot.application.port.persistence.repository.service_state.reader import (
    IServiceStateReader,
)
from universal_bot.application.query_model.service_state import ServiceStateQueryModel
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.value_object.service_state.key import ServiceStateKey
from universal_bot.infrastructure.persistence.sqla.table.service_state import (
    service_state_table as table,
)
from universal_bot.infrastructure.persistence.sqla.type import ReaderSession


class SQLAServiceStateReader(IServiceStateReader):
    def __init__(self, session: ReaderSession) -> None:
        self._session = session

    async def find_by_id(
        self, *, key: ServiceStateKey
    ) -> ServiceStateQueryModel | None:
        key_raw = convert_to_primitive(key)
        row = (
            (
                await self._session.execute(
                    select(table).where(table.c.key == key_raw).limit(1)
                )
            )
            .mappings()
            .first()
        )
        return ServiceStateQueryModel(**row) if row else None
