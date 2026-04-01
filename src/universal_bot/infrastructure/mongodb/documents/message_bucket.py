from datetime import datetime

from pydantic import BaseModel, Field

from universal_bot.infrastructure.mongodb.documents.message import MessageDocument


class MessageBucketDocument(BaseModel):
    id_: str = Field(alias="_id")
    chat_id: int
    seq: int
    messages: list[MessageDocument] = Field(default_factory=list)
    count: int = 0
    created_at: datetime
    updated_at: datetime
