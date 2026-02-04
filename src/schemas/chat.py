from pydantic import BaseModel, Field

from src.schemas.message_roles import MessageRoles


class MessageSchema(BaseModel):
    '''
    Base schema of one message
    '''
    role: MessageRoles
    content: str = Field(None, max_length=10000)


class HistorySchema(BaseModel):
    '''
    Schema of chat history
    '''
    messages: list[MessageSchema] = Field(default_factory=list)


class BaseChatSchema(BaseModel):
    user_id: int
    content: str = Field(..., max_length=10000)


class ResponseSchema(BaseChatSchema):
    tokens_used: int | None = None


class RequestSchema(BaseChatSchema):
    temperature: float = Field(0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(1000, ge=1, le=100000)
