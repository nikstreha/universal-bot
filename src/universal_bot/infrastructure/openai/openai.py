import logging
from dataclasses import asdict
from typing import cast

from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam

from universal_bot.application.dto.ai_chat.request import (
    HistoryDTO,
    MessageDTO,
    RequestDTO,
)
from universal_bot.application.dto.ai_chat.response import ResponseDTO
from universal_bot.application.port.ai_chat.ai_provider import IAIProvider
from universal_bot.domain.enum.message.role import MessageRole as Role

logger = logging.getLogger(__name__)


class OpenAIProvider(IAIProvider):
    def __init__(self, model_token: str, base_url: str) -> None:
        self.model_token = model_token
        self.base_url = base_url

    async def connect(self) -> None:
        if self.client is not None:
            return
        self.client = AsyncOpenAI(
            api_key=self.model_token,
            base_url=self.base_url,
        )

    async def generate(
        self,
        request: RequestDTO,
        history: HistoryDTO,
    ) -> ResponseDTO:
        try:
            openai_messages = cast(
                list[ChatCompletionMessageParam], 
                [asdict(m) for m in history.messages]
            )

            openai_messages.append(
                cast(ChatCompletionMessageParam, asdict(MessageDTO(role=Role.USER, content=request.content)))
            )

            resp = await self.client.chat.completions.create(
                model=request.chat_model,
                messages=openai_messages,
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
