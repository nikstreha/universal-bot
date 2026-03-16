from datetime import datetime

from pydantic import BaseModel

from src.universal_bot.domain.enum.user.role import UserRole


class MessageDocument(BaseModel):
    id: str
    role: UserRole
    content: str
    token_used: int | None = None
    reply_from: str | None = None
    created_at: datetime
