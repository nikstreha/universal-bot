from abc import ABC, abstractmethod

from universal_bot.application.query_model.service_state import ServiceStateQueryModel
from universal_bot.domain.value_object.service_state.key import ServiceStateKey


class IServiceStateReader(ABC):
    @abstractmethod
    async def find_by_id(
        self, *, key: ServiceStateKey
    ) -> ServiceStateQueryModel | None: ...
