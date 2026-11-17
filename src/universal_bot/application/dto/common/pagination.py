from dataclasses import dataclass


@dataclass(frozen=True, slots=True, kw_only=True)
class PaginatedResponse[T]:
    items: list[T]
    next_cursor: str | None
