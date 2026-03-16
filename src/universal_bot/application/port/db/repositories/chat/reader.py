from abc import ABC, abstractmethod

from universal_bot.infrastructure.mongodb.documents.chat import ChatDocument
from universal_bot.infrastructure.mongodb.documents.message import MessageDocument


class IMyChatReader(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: str) -> ChatDocument | None: ...

    @abstractmethod
    async def get_messages(
        self, user_id: str, limit: int = 20
    ) -> list[MessageDocument]: ...
