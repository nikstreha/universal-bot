from dataclasses import dataclass
from datetime import date

from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.common import InvalidRequestError


@dataclass(frozen=True, slots=True)
class FileFilterDTO:
    state: str = "active"
    collection: str = ""
    kind: str = ""
    q: str = ""
    date_from: str = ""
    date_to: str = ""

    def __post_init__(self) -> None:
        ensure(
            self.state in ("active", "trashed"), InvalidRequestError, "Неверный раздел"
        )
        ensure(
            self.collection in ("", "media", "files"),
            InvalidRequestError,
            "Неверная коллекция",
        )
        ensure(
            self.kind in ("", "photo", "video", "audio", "other"),
            InvalidRequestError,
            "Неверный тип файла",
        )
        ensure(
            len(self.q) <= 200, InvalidRequestError, "Слишком длинный поисковый запрос"
        )
        for value in (self.date_from, self.date_to):
            if value:
                try:
                    ensure(
                        date.fromisoformat(value).isoformat() == value,
                        InvalidRequestError,
                        "Неверная дата",
                    )
                except ValueError as exc:
                    raise InvalidRequestError("Неверная дата") from exc
