from abc import ABC, abstractmethod
from typing import BinaryIO


class IObjectStorage(ABC):
    @abstractmethod
    def ready(self) -> None: ...

    @abstractmethod
    def guard(self, needed: int = 0) -> None: ...

    @abstractmethod
    def put(
        self, key: str, data: bytes, mime: str = "application/octet-stream"
    ) -> None: ...

    @abstractmethod
    def compose(self, key: str, parts: list[str]) -> None: ...

    @abstractmethod
    def read(self, key: str, offset: int = 0, length: int = 0) -> BinaryIO: ...

    @abstractmethod
    def size(self, key: str) -> int: ...

    @abstractmethod
    def delete(self, key: str) -> None: ...

    @abstractmethod
    def download(self, key: str, path: str) -> None: ...

    @abstractmethod
    def close(self, response: BinaryIO) -> None: ...

    @abstractmethod
    def inspect(self, key: str) -> tuple[int, str, bytes]: ...
