from datetime import datetime

from pydantic import BaseModel, Field

from universal_bot.infrastructure.mongodb.documents.message import MessageDocument


class ChatDocument(BaseModel):
    id_: int = Field(alias="_id")
    user_id: int
    messages: list[MessageDocument] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
