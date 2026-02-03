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

    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str
    REDIS_USER: str
    REDIS_DB: int

    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_ROOT_USER: str
    MONGO_ROOT_PASSWORD: str

    CONNECT_RETRIES: int = 3
    CONNECT_TIMEOUT: float = 3.0
    CONNECT_BACKOFF_BASE: float = 0.5
    OPERATION_RETRIES: int = 3
    OPERATION_TIMEOUT: float = 5.0

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )

    @property
    def minio_endpoint(self) -> str:
        return f"{self.MINIO_HOST}:{self.MINIO_PORT}"

    @property
    def redis_url(self) -> str:
        return f"redis://{self.REDIS_USER}:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def mongo_url(self) -> str:
        return f"mongodb://{self.MONGO_ROOT_USER}:{self.MONGO_ROOT_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}/?authSource=admin"


settings = Settings()
