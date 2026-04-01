from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic import BaseModel, Field


@dataclass(frozen=True)
class GetAdminMessagesDTO:
    cursor: int = 0


class CacheMessage(BaseModel):
    user_id: int
    message: str | None = None


class UnknownMessageDTO(BaseModel):
    user_id: int
    message: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SuperAdminMessageList(BaseModel):
    messages: list[UnknownMessageDTO] = Field(default_factory=list)
    next_cursor: int | None
