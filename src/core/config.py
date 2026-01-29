from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    MODEL_TOKEN: str
    PROXYAPI_BASE_URL: str
    EMBEDDING_MODEL: str
    CHAT_MODEL: str

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


settings = Settings()
