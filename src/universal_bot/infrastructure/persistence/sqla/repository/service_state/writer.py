from universal_bot.application.port.persistence.repository.service_state.writer import (
    IServiceStateWriter,
)
from universal_bot.domain.common.util import convert_to_primitive
from universal_bot.domain.entity.service_state import ServiceState
from universal_bot.domain.value_object.service_state.key import ServiceStateKey
from universal_bot.infrastructure.persistence.sqla.type import WriterSession


class SQLAServiceStateWriter(IServiceStateWriter):
    def __init__(self, session: WriterSession) -> None:
        self._session = session

    async def find_by_id(self, *, key: ServiceStateKey) -> ServiceState | None:
        key_raw = convert_to_primitive(key)
        return await self._session.get(ServiceState, key_raw)

    async def add(self, *, entity: ServiceState) -> None:
        self._session.add(entity)
        await self._session.flush()
