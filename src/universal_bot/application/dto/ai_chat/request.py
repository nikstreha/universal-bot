from dataclasses import dataclass

from src.universal_bot.domain.enum.message.role import MessageRole as Role


@dataclass(frozen=True)
class RequestDTO:
    user_id: int
    content: str
    max_tokens: int
    temperature: float
    chat_model: str = "gpt-5-mini"


@dataclass(frozen=True)
class MessageDTO:
    role: Role
    content: str


@dataclass(frozen=True)
class HistoryDTO:
    messages: list[MessageDTO]
