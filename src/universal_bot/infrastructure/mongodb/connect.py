from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase


class MongoConnector:
    def __init__(self, url: str, db_name: str) -> None:
        self.url = url
        self.db_name = db_name

    def up(self) -> AsyncDatabase:
        self.client = AsyncMongoClient(self.url)
        self.db = self.client[self.db_name]
        return self.db

    async def down(self) -> None:
        await self.client.close()
