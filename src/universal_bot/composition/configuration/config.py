from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str

    MODEL_TOKEN: str
    PROXYAPI_BASE_URL: str
    EMBEDDING_MODEL: str
    CHAT_MODEL: str

    MINIO_ROOT_USER: str
    MINIO_ROOT_PASSWORD: str
    MINIO_HOST: str
    MINIO_PORT: int
    MINIO_BUCKET: str

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_USER: str
    REDIS_DB: int

    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_ROOT_USER: str
    MONGO_ROOT_PASSWORD: str
    MONGO_DB_NAME: str

    MAX_HISTORY: int = 1000

    MESSAGE_FOR_ADMIN_PAGE_SIZE: int = 20

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="forbid"
    )

    @cached_property
    def minio_endpoint(self) -> str:
        return f"{self.MINIO_HOST}:{self.MINIO_PORT}"

    @cached_property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @cached_property
    def mongo_url(self) -> str:
        return f"mongodb://{self.MONGO_ROOT_USER}:{self.MONGO_ROOT_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/?authSource=admin"
