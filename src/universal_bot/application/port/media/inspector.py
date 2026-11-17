from abc import ABC, abstractmethod


class IMediaInspector(ABC):
    @abstractmethod
    def classify(self, header: bytes) -> tuple[str, str]: ...
