from datetime import datetime

from pydantic import BaseModel, Field
from src.schemas.chat import MessageSchema


class DBMessageSchema(MessageSchema):
    """Schema of one message in db"""
    time_created: datetime = Field(default_factory=datetime.now)
    tokens_used: int | None = None


class DBHistorySchema(BaseModel):
    """Schema of chat history in db"""
    messages: list[DBMessageSchema] = Field(default_factory=list)
