from datetime import datetime

from pydantic import BaseModel, Field

from universal_bot.domain.enum.message.role import MessageRole


class MessageDocumentDTO(BaseModel):
    id_: int
    role: MessageRole
    content: str
    token_used: int | None = None
    reply_from: int | None = None
    created_at: datetime


class ChatDocumentDTO(BaseModel):
    id_: int = Field(alias="_id")
    tg_chat_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
