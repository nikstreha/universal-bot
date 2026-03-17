from dataclasses import dataclass
from enum import StrEnum


class Status(StrEnum):
    SUCCESS = "success"
    FAIL = "fail"
    PARTIAL_SUCCESS = "partial_success"


@dataclass(frozen=True)
class SaveFileErrorResponceDTO:
    file_name: str
    message: str = "Can't upload file"


@dataclass(frozen=True)
class SaveFilesResponceDTO:
    status: Status
    errors: list[SaveFileErrorResponceDTO] | None = None
