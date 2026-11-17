from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True, kw_only=True)
class SessionQueryModel:
    id: str
    user_id: int
    token_hash: str = field(repr=False)
    installation_id: str
    device_name: str
    created_at: int
    last_seen_at: int
    expires_at: int
    absolute_expires_at: int
    revoked_at: int | None = None
