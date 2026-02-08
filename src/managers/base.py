from src.clients.minio_client import get_minio_client
from src.clients.openai import get_openai_client
from src.clients.redis_client import get_redis_client


class BaseManager:
    def __init__(self) -> None:
        self.minio_client = get_minio_client()
        self.redis_client = get_redis_client()
        self.openai_client = get_openai_client()