from datetime import datetime

from pydantic import BaseModel

from universal_bot.domain.enum.message.role import MessageRole


class MessageDocument(BaseModel):
    id_: int
    role: MessageRole
    content: str
    token_used: int | None = None
    reply_from: int | None = None
    created_at: datetime
