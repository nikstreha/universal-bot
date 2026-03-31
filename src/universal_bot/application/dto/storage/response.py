from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    SUCCESS = "success"
    FAIL = "fail"
    PARTIAL_SUCCESS = "partial_success"


@dataclass(frozen=True)
class SaveFileErrorResponseDTO:
    file_name: str
    message: str = "Can't upload file"


@dataclass(frozen=True)
class SaveFilesResponseDTO:
    status: Status
    errors: list[SaveFileErrorResponseDTO] | None = None
