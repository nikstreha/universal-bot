from typing import Literal
from uuid import UUID

from universal_bot.presentation.http.public_api.auth.schema import ProofBody
from universal_bot.presentation.http.public_api.common.schema import (
    ResponseModel,
    UTCDateTime,
)


class AccessBody(ProofBody):
    attempt_id: UUID


class AccessRequestResponse(ResponseModel):
    id: str
    status: str
    source: str
    created_at: UTCDateTime
    decided_at: UTCDateTime | None
    can_request_access: Literal[False] = False


class AccessRequestStatusResponse(ResponseModel):
    status: str
    can_request_access: bool
