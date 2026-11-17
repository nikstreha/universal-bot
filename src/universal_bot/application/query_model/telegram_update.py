from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class TelegramUpdateQueryModel:
    id: int
    payload: str
    created_at: int
    state: str = "queued"
