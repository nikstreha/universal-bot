from abc import ABC, abstractmethod

from universal_bot.domain.entity.administrator import Administrator


class IAdministratorWriter(ABC):
    @abstractmethod
    async def get(self) -> Administrator | None: ...

    @abstractmethod
    async def add(self, *, administrator: Administrator) -> None: ...
