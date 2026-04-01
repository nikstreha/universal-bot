from abc import ABC, abstractmethod

from universal_bot.domain.entity.message_bucket import MessageBucket
from universal_bot.domain.value_object.chat.id import ChatId
from universal_bot.domain.value_object.message.message import Message


class IMessageBucketWriter(ABC):
    @abstractmethod
    async def get_latest_bucket(self, chat_id: ChatId) -> MessageBucket | None: ...

    @abstractmethod
    async def add_message(self, chat_id: ChatId, message: Message) -> None: ...

    @abstractmethod
    async def delete_by_chat_id(self, chat_id: ChatId) -> None: ...
