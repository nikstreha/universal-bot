from abc import ABC, abstractmethod

from universal_bot.application.dto.telegram.message import TelegramMessageDTO


class ITelegramClient(ABC):
    @abstractmethod
    async def set_webhook(self, *, url: str, secret: str) -> None: ...

    @abstractmethod
    async def delete_webhook(self) -> None: ...

    @abstractmethod
    async def get_updates(self, *, offset: int, timeout: int = 30) -> list[dict]: ...

    @abstractmethod
    async def message(
        self,
        chat_id: int,
        text: str,
        keyboard: dict | None = None,
        reply_to: int | None = None,
    ) -> TelegramMessageDTO: ...

    @abstractmethod
    async def document(
        self, chat_id: int, text: str, filename: str, reply_to: int | None = None
    ) -> TelegramMessageDTO: ...

    @abstractmethod
    async def edit_message(
        self, chat_id: int, message_id: int, text: str
    ) -> TelegramMessageDTO: ...

    @abstractmethod
    async def edit_document(
        self, chat_id: int, message_id: int, text: str, filename: str
    ) -> TelegramMessageDTO: ...

    @abstractmethod
    async def answer(self, callback_id: str) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...
