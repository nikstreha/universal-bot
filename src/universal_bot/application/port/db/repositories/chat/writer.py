from abc import ABC, abstractmethod

from universal_bot.domain.entity.chat import Chat
from universal_bot.domain.value_object.chat.id import ChatId


class IChatWriter(ABC):
    @abstractmethod
    async def get_by_id(self, chat_id: ChatId) -> Chat | None: ...

    @abstractmethod
    async def create(self, chat: Chat) -> None: ...

    @abstractmethod
    async def delete(self, chat_id: ChatId) -> None: ...
