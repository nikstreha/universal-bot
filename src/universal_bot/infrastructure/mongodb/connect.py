from types import TracebackType

from pymongo import AsyncMongoClient


class MongoConnector:
    def __init__(self, url: str) -> None:
        self.url = url

    def up(self) -> AsyncMongoClient:
        self._client = AsyncMongoClient(self.url)
        return self._client

    async def down(self) -> None:
        await self._client.close()

    async def __aenter__(self) -> AsyncMongoClient:
        self.up()
        return self._client

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        await self.down()
