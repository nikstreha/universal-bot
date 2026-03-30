import json
from datetime import datetime

from universal_bot.application.dto.cache.cache_key import CacheKey
from universal_bot.application.dto.messages.unknown import (
    CacheMessage,
    GetAdminMessagesDTO,
    SuperAdminMessageList,
    UnknownMessageDTO,
)
from universal_bot.application.port.cache.cache_provider import ICacheProvider


class GetAdminMessagesInteractor:
    def __init__(self, cache_provider: ICacheProvider, page_size: int):
        self._cache_provider = cache_provider
        self._page_size = page_size

    @staticmethod
    def parse_created_at(key: str) -> datetime:
        iso_part = key.removeprefix(f"{CacheKey.MESSAGES_FOR_ADMIN}:")
        return datetime.fromisoformat(iso_part)

    async def __call__(self, query: GetAdminMessagesDTO) -> SuperAdminMessageList:
        pattern = f"{CacheKey.MESSAGES_FOR_ADMIN}:*"
        keys = await self._cache_provider.keys(pattern)

        keys.sort()

        offset = query.cursor
        page_keys = keys[offset : offset + self._page_size]
        next_cursor = (
            offset + self._page_size if offset + self._page_size < len(keys) else None
        )

        messages: list[UnknownMessageDTO] = []
        for key in page_keys:
            raw = await self._cache_provider.get(key)
            if raw is None:
                continue
            try:
                data: dict = json.loads(raw)
                cache_message = CacheMessage(**data)

                created_at = self.parse_created_at(key)
                messages.append(
                    UnknownMessageDTO(
                        user_id=cache_message.user_id,
                        message=cache_message.message,
                        created_at=created_at,
                    )
                )
            except (ValueError, KeyError):
                continue

        return SuperAdminMessageList(messages=messages, next_cursor=next_cursor)
