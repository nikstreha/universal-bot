from dataclasses import dataclass


@dataclass(frozen=True)
class DeleteFileDTO:
    bucket_name: str
    object_name: str
