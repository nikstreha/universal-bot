from dataclasses import dataclass

from src.backend_component.domain.enum.user.role import UserRole


@dataclass(frozen=True)
class RequestDTO:
    user_id: int
    content: str
    max_tokens: int
    temperature: float


@dataclass(frozen=True)
class MessageDTO:
    role: UserRole
    content: str


@dataclass(frozen=True)
class HistoryDTO:
    messages: list[MessageDTO]
