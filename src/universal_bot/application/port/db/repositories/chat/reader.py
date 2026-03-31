from abc import ABC, abstractmethod

from universal_bot.application.dto.ai_chat.documents import (
    ChatDocumentDTO,
    MessageDocumentDTO,
)


class IMyChatReader(ABC):
    @abstractmethod
    async def get_by_user_id(self, user_id: int) -> ChatDocumentDTO | None: ...

    @abstractmethod
    async def get_messages(
        self, user_id: int, limit: int = 20
    ) -> list[MessageDocumentDTO]: ...
