from abc import ABC, abstractmethod

from backend_component.composition.configuration.config import settings
from src.backend_component.application.dto.ai_chat.request import HistoryDTO, RequestDTO
from src.backend_component.application.dto.ai_chat.response import ResponseDTO


class IAIProvider(ABC):
    @abstractmethod
    async def generate(
        self, request: RequestDTO, history: HistoryDTO,
    ) -> ResponseDTO:
        ...
