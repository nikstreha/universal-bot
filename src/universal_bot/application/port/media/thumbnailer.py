from abc import ABC, abstractmethod


class IThumbnailer(ABC):
    @abstractmethod
    def create(
        self, object_key: str, target_key: str, media_kind: str, size_bytes: int
    ) -> None: ...
