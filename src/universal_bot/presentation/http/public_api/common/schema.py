from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict

from universal_bot.domain.common.util import convert_to_primitive


def _utc_datetime(value):
    value = convert_to_primitive(value)
    return datetime.fromtimestamp(value, UTC) if isinstance(value, int) else value


UTCDateTime = Annotated[datetime, BeforeValidator(_utc_datetime)]


class ResponseModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class PageResponse[T](ResponseModel):
    items: list[T]
    next_cursor: str | None
