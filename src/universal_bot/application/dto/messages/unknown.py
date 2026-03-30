from dataclasses import dataclass
from datetime import datetime

from pydantic import BaseModel, Field

from universal_bot.application.dto.cache.cache_key import CacheKey


@dataclass(frozen=True)
class GetAdminMessagesDTO:
    cursor: int = 0


class CacheMessage(BaseModel):
    user_id: int
    message: str | None = None


class UnknownMessageDTO(CacheMessage):
    created_at: datetime = Field(default_factory=datetime.now)

    def build_cache_key(self) -> str:
        return f"{CacheKey.MESSAGES_FOR_ADMIN}:{self.created_at.isoformat()}"


class SuperAdminMessageList(BaseModel):
    messages: list[UnknownMessageDTO] = Field(default_factory=list)
    next_cursor: int | None
