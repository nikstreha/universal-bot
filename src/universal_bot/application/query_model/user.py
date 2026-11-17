from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class UserQueryModel:
    id: int
    name: str = ""
    created_at: int = 0
    last_seen_at: int = 0


@dataclass(frozen=True, slots=True, kw_only=True)
class AdminUserQueryModel:
    id: int
    name: str
    files: int
    bytes: int
