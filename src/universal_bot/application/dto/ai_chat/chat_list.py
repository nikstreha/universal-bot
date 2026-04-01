from pydantic import BaseModel, Field

from universal_bot.application.dto.ai_chat.documents import ChatDocumentDTO


class GetChatsByUserIdRequestDTO(BaseModel):
    user_id: int
    limit: int = Field(default=20, ge=1, le=100)
    after_id: int | None = None


class GetChatsByTgChatIdRequestDTO(BaseModel):
    tg_chat_id: int
    limit: int = Field(default=20, ge=1, le=100)
    after_id: int | None = None


class GetChatsResponseDTO(BaseModel):
    chats: list[ChatDocumentDTO]
    after_id: int | None = None
