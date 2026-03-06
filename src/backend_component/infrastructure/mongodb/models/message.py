from datetime import datetime
from pydantic import BaseModel


class MessageDocument(BaseModel):
    id: str
    role: str
    content: str
    token_used: int | None = None
    reply_from: str | None = None
    created_at: datetime