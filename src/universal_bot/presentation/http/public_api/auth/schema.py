from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from universal_bot.presentation.http.public_api.common.schema import (
    ResponseModel,
    UTCDateTime,
)


class AttemptBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code_challenge: str = Field(pattern="^[A-Za-z0-9_-]{43}$")
    installation_id: str = Field(min_length=1, max_length=100)
    device_name: str = Field(default="Android", max_length=100)


class ProofBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    code_verifier: str = Field(pattern="^[A-Za-z0-9._~-]{43,128}$")


class LoginAttemptResponse(ResponseModel):
    attempt_id: str
    authorization_url: str
    login_code: str
    expires_at: UTCDateTime


class LoginUserResponse(ResponseModel):
    id: str
    name: str
    is_admin: bool


class PendingLoginResponse(ResponseModel):
    state: Literal["pending"] = "pending"


class AuthenticatedSessionResponse(ResponseModel):
    session_token: str = Field(repr=False)
    session_id: str
    expires_at: UTCDateTime
    absolute_expires_at: UTCDateTime
    user: LoginUserResponse
