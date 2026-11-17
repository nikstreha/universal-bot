from abc import ABC, abstractmethod


class ISpeechRecognizer(ABC):
    @abstractmethod
    def transcribe(self, telegram_file_id: str) -> str: ...
