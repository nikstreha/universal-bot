import logging
from dataclasses import asdict


from openai import AsyncOpenAI

from backend_component.domain.enum.user.role import UserRole
from backend_component.application.dto.ai_chat.request import RequestDTO, HistoryDTO, MessageDTO
from backend_component.application.dto.ai_chat.response import ResponseDTO
from backend_component.application.ai_chat.ai_provider import IAIProvider

logger = logging.getLogger(__name__)


class OpenAIProvider(IAIProvider):
    def __init__(self, model_token: str, base_url: str) -> None:
        self.client: AsyncOpenAI | None = None
        self.model_token = model_token
        self.base_url = base_url

    async def connect(self) -> None:
        if self.client is not None:
            return
        self.client = AsyncOpenAI(
            api_key=self.model_token, base_url=self.base_url,
        )

    async def generate(
        self, request: RequestDTO, history: HistoryDTO,
    ) -> ResponseDTO:
        
        try:
            messages = [
                asdict(message) for message in history.messages
            ]
            messages.append(asdict(MessageDTO(role=UserRole.USER, content=request.content)))

            resp = await self.client.chat.completions.create(
                model=request.chat_model,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )

            content = resp.choices[0].message.content or ""

            return ResponseDTO(
                user_id=request.user_id,
                content=content,
                tokens_used=resp.usage.total_tokens if resp.usage else None,
            )
        
        except Exception:
            logger.exception("OpenAI generate error")
            raise
