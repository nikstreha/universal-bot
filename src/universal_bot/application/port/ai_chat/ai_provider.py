from abc import ABC, abstractmethod

from universal_bot.application.dto.ai_chat.request import HistoryDTO, RequestDTO
from universal_bot.application.dto.ai_chat.response import ResponseDTO


class IAIProvider(ABC):
    @abstractmethod
    async def generate(
        self,
        request: RequestDTO,
        history: HistoryDTO | None = None,
    ) -> ResponseDTO: ...
