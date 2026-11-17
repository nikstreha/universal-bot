from abc import ABC, abstractmethod
from collections.abc import Sequence

from universal_bot.domain.entity.job import Job
from universal_bot.domain.enum.job.kind import JobKind
from universal_bot.domain.value_object.job.deduplication_key import DeduplicationKey
from universal_bot.domain.value_object.job.id import JobId
from universal_bot.domain.value_object.time.timestamp import Timestamp


class IJobWriter(ABC):
    @abstractmethod
    async def find_next_available(
        self, *, kinds: Sequence[JobKind], at: Timestamp
    ) -> Job | None: ...

    @abstractmethod
    async def find_by_id(self, *, key: JobId) -> Job | None: ...

    @abstractmethod
    async def find_by_dedup_key(self, *, dedup_key: DeduplicationKey) -> Job | None: ...

    @abstractmethod
    async def add(self, *, entity: Job) -> None: ...
