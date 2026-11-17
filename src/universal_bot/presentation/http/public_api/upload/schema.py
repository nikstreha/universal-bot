from typing import Self

from pydantic import BaseModel, ConfigDict, Field

from universal_bot.application.query_model.upload import UploadQueryModel
from universal_bot.application.query_model.upload_part import UploadPartQueryModel
from universal_bot.domain.enum.upload.state import UploadState
from universal_bot.presentation.http.public_api.common.schema import (
    ResponseModel,
    UTCDateTime,
)


class UploadBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    original_name: str = Field(min_length=1, max_length=255)
    size_bytes: int = Field(ge=0)
    sha256: str = Field(pattern="^[a-f0-9]{64}$")
    declared_mime: str = Field(default="application/octet-stream", max_length=150)


class UploadResponse(ResponseModel):
    upload_id: str
    state: UploadState
    part_size_bytes: int
    part_count: int
    received_parts: list[int]
    received_bytes: int
    expires_at: UTCDateTime
    file_id: str | None
    error: str | None
    storage_date: str
    storage_timezone: str
    archive_path: str

    @classmethod
    def from_upload(
        cls, pair: tuple[UploadQueryModel, list[UploadPartQueryModel]]
    ) -> Self:
        upload, parts = pair
        return cls(
            upload_id=upload.id,
            state=upload.state,
            part_size_bytes=upload.part_bytes,
            part_count=upload.part_count,
            received_parts=[part.part_index for part in parts],
            received_bytes=sum(part.size_bytes for part in parts),
            expires_at=upload.expires_at,
            file_id=upload.file_id,
            error=upload.error,
            storage_date=upload.storage_date,
            storage_timezone=upload.storage_timezone,
            archive_path=upload.storage_date.replace("-", "/"),
        )
