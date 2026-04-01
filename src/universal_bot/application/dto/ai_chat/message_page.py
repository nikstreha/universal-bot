from pydantic import BaseModel, Field

from universal_bot.application.dto.ai_chat.documents import MessageDocumentDTO


class MessageCursor(BaseModel):
    seq: int
    index: int


class GetMessagesRequestDTO(BaseModel):
    chat_id: int
    limit: int = Field(default=20, ge=1, le=100)
    cursor: MessageCursor | None = None


class GetMessagesResponseDTO(BaseModel):
    messages: list[MessageDocumentDTO]
    next_cursor: MessageCursor | None = None
