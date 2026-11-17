from abc import ABC, abstractmethod

from universal_bot.domain.entity.administrator import Administrator


class IAdministratorReader(ABC):
    @abstractmethod
    async def get(self) -> Administrator | None: ...
