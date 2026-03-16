from abc import ABC, abstractmethod

from universal_bot.domain.entity.chat import MyChat
from universal_bot.domain.value_object.message.message import Message
from universal_bot.domain.value_object.user.id import UserId


class IMyChatWriter(ABC):
    @abstractmethod
    async def replace(self, chat: MyChat) -> None: ...

    @abstractmethod
    async def add_message(self, user_id: UserId, message: Message) -> None: ...

    @abstractmethod
    async def create(self, chat: MyChat) -> None: ...
