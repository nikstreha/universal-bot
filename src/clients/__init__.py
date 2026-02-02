from typing import Protocol, runtime_checkable


@runtime_checkable
class ConnectableClient(Protocol):
    async def connect(self) -> None: ...

Clients = ConnectableClient
