from dataclasses import dataclass


@dataclass(frozen=True)
class ResponseDTO:
    user_id: int
    content: str
    tokens_used: int | None = None
