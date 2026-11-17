from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminNotificationQueryModel:
    id: str
    event_key: str
    user_id: int
    source: str
    outcome: str
    created_at: int
    read_at: int | None = None
