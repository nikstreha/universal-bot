from abc import ABC, abstractmethod


class IClock(ABC):
    @abstractmethod
    def now(self) -> int: ...

    @abstractmethod
    def archive_date(self, timezone: str) -> str: ...
