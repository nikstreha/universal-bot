from universal_bot.domain.entity.common import Entity
from universal_bot.domain.exception.common import RateLimitedError
from universal_bot.domain.value_object.rate_limit.key import RateLimitKey
from universal_bot.domain.value_object.time.timestamp import Timestamp


class RateLimit(Entity[RateLimitKey]):
    _identity_field = "key"
    key: RateLimitKey
    window_start: Timestamp
    count: int

    def __init__(
        self, *, key: RateLimitKey, window_start: Timestamp, count: int = 1
    ) -> None:
        super().__init__(id_=key)
        self.window_start = window_start
        self.count = count

    @property
    def key(self) -> RateLimitKey:
        return self.id_

    def consume(self, *, maximum: int, seconds: int, at: Timestamp) -> None:
        if self.window_start.value <= at.value - seconds:
            self.window_start, self.count = (at, 1)
        elif self.count < maximum:
            self.count += 1
        else:
            raise RateLimitedError("Слишком много запросов", retry_after=seconds)
