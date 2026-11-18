from abc import ABC, abstractmethod


class IObjectStream(ABC):
    @abstractmethod
    async def read(self, size: int = -1) -> bytes: ...

    @abstractmethod
    async def close(self) -> None: ...


class IObjectStorage(ABC):
    @abstractmethod
    async def ready(self) -> None: ...

    @abstractmethod
    async def guard(self, needed: int = 0) -> None: ...

    @abstractmethod
    async def put(
        self, key: str, data: bytes, mime: str = "application/octet-stream"
    ) -> None: ...

    @abstractmethod
    async def compose(self, key: str, parts: list[str]) -> None: ...

    @abstractmethod
    async def read(
        self, key: str, offset: int = 0, length: int = 0
    ) -> IObjectStream: ...

    @abstractmethod
    async def size(self, key: str) -> int: ...

    @abstractmethod
    async def delete(self, key: str) -> None: ...

    @abstractmethod
    async def download(self, key: str, path: str) -> None: ...

    @abstractmethod
    async def close(self, response: IObjectStream) -> None: ...

    @abstractmethod
    async def inspect(self, key: str) -> tuple[int, str, bytes]: ...
