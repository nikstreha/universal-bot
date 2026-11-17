from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AccessRequestQueryModel:
    id: str
    user_id: int
    source: str
    created_at: int
    status: str = "pending"
    decided_at: int | None = None
    decided_by: int | None = None
