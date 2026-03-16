from dataclasses import Field
from datetime import datetime

from pydantic import BaseModel

from universal_bot.infrastructure.mongodb.documents.message import MessageDocument


class ChatDocument(BaseModel):
    id_: str = Field(alias="_id")
    user_id: str
    messages: list[MessageDocument] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
