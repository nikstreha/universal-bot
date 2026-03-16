from dataclasses import dataclass


@dataclass(frozen=True)
class CacheDataDTO:
    key: str
    value: str
    expire: int | None = None
