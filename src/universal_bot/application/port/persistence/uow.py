from abc import ABC, abstractmethod
from types import TracebackType


class IUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self) -> IUnitOfWork: ...

    @abstractmethod
    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None: ...

    @abstractmethod
    async def flush(self) -> None: ...
