from abc import ABC, abstractmethod

from universal_bot.application.dto.ai_chat.bucket import MessageBucketDTO
from universal_bot.application.dto.ai_chat.message_page import (
    GetMessagesRequestDTO,
    GetMessagesResponseDTO,
)


class IMessageBucketReader(ABC):
    @abstractmethod
    async def get_messages(
        self, request: GetMessagesRequestDTO
    ) -> GetMessagesResponseDTO: ...

    @abstractmethod
    async def get_buckets_by_chat(self, chat_id: int) -> list[MessageBucketDTO]: ...
