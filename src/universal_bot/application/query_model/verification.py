from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class VerificationQueryModel:
    id: str
    file_id: str
    operation_key: str
    state: str = "queued"
    checked_at: int | None = None
    observed_sha256: str | None = None
    observed_size: int | None = None
    integrity: str | None = None
    error: str | None = None
