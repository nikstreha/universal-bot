from abc import ABC, abstractmethod

from universal_bot.domain.entity.service_state import ServiceState
from universal_bot.domain.value_object.service_state.key import ServiceStateKey


class IServiceStateWriter(ABC):
    @abstractmethod
    async def find_by_id(self, *, key: ServiceStateKey) -> ServiceState | None: ...

    @abstractmethod
    async def add(self, *, entity: ServiceState) -> None: ...
