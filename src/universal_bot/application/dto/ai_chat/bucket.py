from datetime import datetime

from pydantic import BaseModel, Field

from universal_bot.application.dto.ai_chat.documents import MessageDocumentDTO


class MessageBucketDTO(BaseModel):
    id_: str = Field(alias="_id")
    chat_id: int
    seq: int
    messages: list[MessageDocumentDTO] = Field(default_factory=list)
    count: int
    created_at: datetime
    updated_at: datetime
