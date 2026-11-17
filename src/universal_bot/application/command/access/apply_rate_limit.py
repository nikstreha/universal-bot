from universal_bot.application.port.clock import IClock
from universal_bot.application.port.persistence.repository.rate_limit.writer import (
    IRateLimitWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.domain.entity.rate_limit import RateLimit
from universal_bot.domain.value_object.rate_limit.key import RateLimitKey
from universal_bot.domain.value_object.time.timestamp import Timestamp


class ApplyRateLimitInteractor:
    def __init__(
        self, *, clock: IClock, rate_limit_writer: IRateLimitWriter, uow: IUnitOfWork
    ) -> None:
        self._clock = clock
        self._rate_limit_writer = rate_limit_writer
        self._uow = uow

    async def __call__(self, *, key: str, maximum: int = 30, seconds: int = 60) -> None:
        async with self._uow:
            await self._rate_limit_writer.delete_stale(
                before=Timestamp(self._clock.now() - max(120, seconds * 2))
            )
            row = await self._rate_limit_writer.find_by_id(key=RateLimitKey(key))
            if row is None:
                await self._rate_limit_writer.add(
                    entity=RateLimit(
                        key=RateLimitKey(key), window_start=Timestamp(self._clock.now())
                    )
                )
            else:
                row.consume(
                    maximum=maximum, seconds=seconds, at=Timestamp(self._clock.now())
                )
