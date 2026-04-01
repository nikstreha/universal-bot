from dataclasses import dataclass

from universal_bot.domain.enum.message.role import MessageRole as Role


@dataclass(frozen=True)
class RequestDTO:
    user_id: int
    content: str
    max_tokens: int
    temperature: float
    chat_model: str = "gpt-5-mini"

    def __post_init__(self):
        if self.max_tokens <= 0:
            raise ValueError("max_tokens must be greater than 0")
        if self.temperature < 0 or self.temperature > 2:
            raise ValueError("temperature must be between 0 and 2")


@dataclass(frozen=True)
class MessageDTO:
    role: Role
    content: str


@dataclass(frozen=True)
class HistoryDTO:
    messages: list[MessageDTO]
