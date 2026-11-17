from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class AccessGrantQueryModel:
    user_id: int
    added_at: int
    added_by: int
