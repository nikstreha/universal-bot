import json

from universal_bot.application.dto.cache.cache_data import CacheDataDTO
from universal_bot.application.dto.cache.cache_key import CacheKey
from universal_bot.application.dto.messages.unknown import (
    CacheMessage,
    UnknownMessageDTO,
)
from universal_bot.application.port.cache.cache_provider import ICacheProvider


class UnknownUserMessageInteractor:
    def __init__(self, cache_provider: ICacheProvider):
        self._cache_provider = cache_provider

    async def __call__(self, unknown_msg: UnknownMessageDTO) -> None:
        cache_msg = CacheMessage(
            user_id=unknown_msg.user_id,
            message=unknown_msg.message,
        )
        await self._cache_provider.set(
            CacheDataDTO(
                key=unknown_msg.cache_key,
                value=json.dumps(cache_msg.model_dump()),
                expire=60 * 60 * 24 * 7,
            ),
        )
