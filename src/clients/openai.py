import logging
from typing import List, Optional

from openai import AsyncOpenAI
from src.core.config import settings
from src.schemas.chat import HistorySchema, RequestSchema, ResponseSchema

logger = logging.getLogger(__name__)


class OpenAIClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.MODEL_TOKEN, base_url=settings.PROXYAPI_BASE_URL
        )

    async def embedding(
        self, text: str, model: str = settings.EMBEDDING_MODEL
    ) -> Optional[List[float]]:
        text = text.strip()
        if not text:
            return None

        try:
            response = await self.client.embeddings.create(input=text, model=model)
            return response.data[0].embedding
        except Exception as e:
            logger.error("OpenAI embedding error: %s", e)
            return None
    
    async def generate(
        self,
        request: RequestSchema,
        history: HistorySchema
    ) -> ResponseSchema:
        try:
            messages = [message.model_dump(exclude_none=True) for message in history.messages]
            messages.append({"role": "user", "content": request.content})

            resp = await self.client.chat.completions.create(
                model=settings.CHAT_MODEL,
                messages=messages,
                max_tokens=request.max_tokens,
                temperature=request.temperature,
            )

            content = resp.choices[0].message.content or ""

            return ResponseSchema(
                user_id=request.user_id,
                content=content,
                tokens_used=resp.usage.total_tokens if resp.usage else None
            )
        except Exception as e:
            logger.error("OpenAI generate error: %s", e)
            raise


openai_client = OpenAIClient()
