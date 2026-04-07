import asyncio
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from universal_bot.application.port.storage.upload_limiter import IUploadLimiter


class UploadLimiter(IUploadLimiter):
    def __init__(self, max_concurrent: int) -> None:
        self._semaphore = asyncio.Semaphore(max_concurrent)

    @asynccontextmanager
    async def acquire(self) -> AsyncIterator[None]:
        async with self._semaphore:
            yield
