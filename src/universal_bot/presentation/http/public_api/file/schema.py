from dataclasses import asdict
from typing import Self

from pydantic import computed_field

from universal_bot.application.query_model.stored_file import StoredFileQueryModel
from universal_bot.application.query_model.verification import VerificationQueryModel
from universal_bot.domain.entity.stored_file import StoredFile
from universal_bot.domain.entity.verification import Verification
from universal_bot.domain.enum.file.integrity import FileIntegrity
from universal_bot.domain.enum.file.media_kind import MediaKind
from universal_bot.domain.enum.file.state import FileState
from universal_bot.domain.enum.file.thumbnail_state import ThumbnailState
from universal_bot.domain.enum.verification.state import VerificationState
from universal_bot.presentation.http.public_api.common.schema import (
    ResponseModel,
    UTCDateTime,
)


class FileIntegrityResponse(ResponseModel):
    status: FileIntegrity
    checked_at: UTCDateTime


class FileResponse(ResponseModel):
    id: str
    original_name: str
    size_bytes: int
    sha256: str
    storage_date: str
    storage_timezone: str
    mime_type: str
    media_kind: MediaKind
    state: FileState
    thumbnail_state: ThumbnailState
    created_at: UTCDateTime
    trashed_at: UTCDateTime | None
    purge_after: UTCDateTime | None
    integrity: FileIntegrityResponse

    @computed_field
    @property
    def archive_path(self) -> str:
        return self.storage_date.replace("-", "/")

    @classmethod
    def from_file(cls, file: StoredFile | StoredFileQueryModel) -> Self:
        data = file.to_dict() if isinstance(file, StoredFile) else asdict(file)
        data["integrity"] = {
            "status": data["integrity"],
            "checked_at": data["checked_at"],
        }
        return cls.model_validate(data)


class FileDateGroupResponse(ResponseModel):
    storage_date: str
    file_count: int
    size_bytes: int


class VerificationResponse(ResponseModel):
    id: str
    file_id: str
    operation_key: str
    state: VerificationState
    checked_at: UTCDateTime | None
    observed_sha256: str | None
    observed_size: int | None
    integrity: FileIntegrity | None
    error: str | None

    @computed_field
    @property
    def verification_id(self) -> str:
        return self.id

    @computed_field
    @property
    def size_bytes(self) -> int | None:
        return self.observed_size

    @classmethod
    def from_verification(
        cls, verification: Verification | VerificationQueryModel
    ) -> Self:
        data = (
            verification.to_dict()
            if isinstance(verification, Verification)
            else asdict(verification)
        )
        return cls.model_validate(data)
