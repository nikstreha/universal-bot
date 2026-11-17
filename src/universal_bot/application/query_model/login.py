from dataclasses import dataclass, field
from typing import Literal


@dataclass(frozen=True, slots=True, kw_only=True)
class LoginAttemptQueryModel:
    attempt_id: str
    authorization_url: str
    login_code: str
    expires_at: int


@dataclass(frozen=True, slots=True, kw_only=True)
class LoginUserQueryModel:
    id: str
    name: str
    is_admin: bool


@dataclass(frozen=True, slots=True, kw_only=True)
class PendingLoginQueryModel:
    state: Literal["pending"] = "pending"


@dataclass(frozen=True, slots=True, kw_only=True)
class AuthenticatedSessionQueryModel:
    session_token: str = field(repr=False)
    session_id: str
    expires_at: int
    absolute_expires_at: int
    user: LoginUserQueryModel
