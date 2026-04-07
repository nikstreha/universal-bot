from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator


class IUploadLimiter(ABC):
    @abstractmethod
    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[None]: ...
