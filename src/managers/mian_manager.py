from src.managers.base import BaseManager
from src.schemas.documents.chat import Chat


class MainManager(BaseManager):
    pass


def get_manager() -> MainManager:
    return MainManager()
