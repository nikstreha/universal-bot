from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from pymongo.asynchronous.database import AsyncDatabase

from src.universal_bot.application.port.cache.cache_provider import ICacheProvider
from src.universal_bot.application.port.db.repositories.chat.reader import IMyChatReader
from src.universal_bot.application.port.db.repositories.chat.writer import IMyChatWriter
from src.universal_bot.application.port.db.repositories.user.reader import IUserReader
from src.universal_bot.application.port.db.repositories.user.writer import IUserWriter
from src.universal_bot.application.port.storage.storage_provider import IStorageProvider
from src.universal_bot.composition.configuration.config import Settings
from src.universal_bot.infrastructure.minio.storage import MinioProvider
from src.universal_bot.infrastructure.mongodb.connect import MongoConnector
from src.universal_bot.infrastructure.mongodb.repositories.chat.reader import (
    MyChatReader,
)
from src.universal_bot.infrastructure.mongodb.repositories.chat.writer import (
    MyChatWriter,
)
from src.universal_bot.infrastructure.mongodb.repositories.user.reader import UserReader
from src.universal_bot.infrastructure.mongodb.repositories.user.writer import UserWriter
from src.universal_bot.infrastructure.redis.redis_provider import RedisProvider


class StorageProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_storage(
        self, configuration: Settings
    ) -> AsyncIterator[IStorageProvider]:
        async with MinioProvider(
            endpoint=configuration.minio_endpoint,
            user=configuration.MINIO_ROOT_USER,
            password=configuration.MINIO_ROOT_PASSWORD,
        ) as minio:
            yield minio


class CacheProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_cache(self, configuration: Settings) -> AsyncIterator[ICacheProvider]:
        async with RedisProvider(url=configuration.redis_url) as redis:
            yield redis


class DataBaseProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_db(self, configuration: Settings) -> AsyncIterator[AsyncDatabase]:
        async with MongoConnector(configuration.mongo_url) as client:
            db = client[configuration.MONGO_DB_NAME]
            yield db


class DatabaseRepositoryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_user_reader(self, db: AsyncDatabase) -> IUserReader:
        return UserReader(db)

    @provide
    def get_user_writer(self, db: AsyncDatabase) -> IUserWriter:
        return UserWriter(db)

    @provide
    def get_message_reader(self, db: AsyncDatabase) -> IMyChatReader:
        return MyChatReader(db)

    @provide
    def get_message_writer(self, db: AsyncDatabase) -> IMyChatWriter:
        return MyChatWriter(db)
