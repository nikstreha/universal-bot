from abc import ABC, abstractmethod


class ISecrets(ABC):
    @abstractmethod
    def identity(self) -> str: ...

    @abstractmethod
    def token(self) -> str: ...

    @abstractmethod
    def hash(self, value: str | bytes) -> str: ...

    @abstractmethod
    def challenge(self, verifier: str) -> str: ...

    @abstractmethod
    def matches(self, first: str, second: str) -> bool: ...

    @abstractmethod
    def login_code(self) -> str: ...
