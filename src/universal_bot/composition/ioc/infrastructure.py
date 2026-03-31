from collections.abc import AsyncIterator

from dishka import Provider, Scope, provide
from pymongo.asynchronous.database import AsyncDatabase

from universal_bot.application.port.ai_chat.ai_provider import IAIProvider
from universal_bot.application.port.cache.cache_provider import ICacheProvider
from universal_bot.application.port.db.repositories.chat.reader import IMyChatReader
from universal_bot.application.port.db.repositories.chat.writer import IMyChatWriter
from universal_bot.application.port.db.repositories.user.reader import IUserReader
from universal_bot.application.port.db.repositories.user.writer import IUserWriter
from universal_bot.application.port.storage.storage_provider import IStorageProvider
from universal_bot.composition.configuration.config import Settings
from universal_bot.infrastructure.minio.storage import MinioProvider
from universal_bot.infrastructure.mongodb.connect import MongoConnector
from universal_bot.infrastructure.mongodb.repositories.chat.reader import (
    MyChatReader,
)
from universal_bot.infrastructure.mongodb.repositories.chat.writer import (
    MyChatWriter,
)
from universal_bot.infrastructure.mongodb.repositories.user.reader import UserReader
from universal_bot.infrastructure.mongodb.repositories.user.writer import UserWriter
from universal_bot.infrastructure.openai.openai_provider import OpenAIProvider
from universal_bot.infrastructure.redis.redis_provider import RedisProvider


class AIProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_ai(self, configuration: Settings) -> AsyncIterator[IAIProvider]:
        async with OpenAIProvider(
            model_token=configuration.MODEL_TOKEN,
            base_url=configuration.PROXYAPI_BASE_URL,
        ) as ai:
            yield ai


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
            await minio.check_or_create_bucket(configuration.MINIO_BUCKET)
            yield minio


class CacheProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_cache(self, configuration: Settings) -> AsyncIterator[ICacheProvider]:
        async with RedisProvider(url=configuration.redis_url) as redis:
            yield redis


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_db(self, configuration: Settings) -> AsyncIterator[AsyncDatabase]:
        async with MongoConnector(configuration.mongo_url) as mongo:
            db = mongo.client[configuration.MONGO_DB_NAME]
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


def _infrastructure_provider() -> tuple[Provider, ...]:
    return (
        AIProvider(),
        CacheProvider(),
        DatabaseProvider(),
        DatabaseRepositoryProvider(),
        StorageProvider(),
    )
