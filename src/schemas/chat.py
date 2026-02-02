from enum import Enum

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    TOOL = "tool"


class MessageSchema(BaseModel):
    role: MessageRole
    content: str = Field(None, max_length=10000)


class HistorySchema(BaseModel):
    messages: list[MessageSchema] = Field(default_factory=list)


class BaseChatSchema(BaseModel):
    user_id: int
    content: str = Field(..., max_length=10000)


class ResponseSchema(BaseChatSchema):
    tokens_used: int | None = None


class RequestSchema(BaseChatSchema):
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1000, ge=1, le=100000)
