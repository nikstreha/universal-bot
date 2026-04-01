from abc import ABC, abstractmethod

from universal_bot.application.dto.ai_chat.chat_list import (
    GetChatsByTgChatIdRequestDTO,
    GetChatsByUserIdRequestDTO,
    GetChatsResponseDTO,
)
from universal_bot.application.dto.ai_chat.documents import ChatDocumentDTO


class IChatReader(ABC):
    @abstractmethod
    async def get_by_id(self, chat_id: int) -> ChatDocumentDTO | None: ...

    @abstractmethod
    async def get_by_user_id(
        self, request: GetChatsByUserIdRequestDTO
    ) -> GetChatsResponseDTO: ...

    @abstractmethod
    async def get_by_tg_chat_id(
        self, request: GetChatsByTgChatIdRequestDTO
    ) -> GetChatsResponseDTO: ...
