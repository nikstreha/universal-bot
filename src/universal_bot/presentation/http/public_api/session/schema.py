from universal_bot.presentation.http.public_api.common.schema import (
    ResponseModel,
    UTCDateTime,
)


class SessionResponse(ResponseModel):
    id: str
    device_name: str
    created_at: UTCDateTime
    last_seen_at: UTCDateTime
    expires_at: UTCDateTime
    is_current: bool


class SessionCollectionResponse(ResponseModel):
    items: list[SessionResponse]
