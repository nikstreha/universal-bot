from abc import ABC, abstractmethod

from universal_bot.application.query_model.verification import VerificationQueryModel
from universal_bot.domain.value_object.verification.id import VerificationId


class IVerificationReader(ABC):
    @abstractmethod
    async def find_by_id(
        self, *, key: VerificationId
    ) -> VerificationQueryModel | None: ...
