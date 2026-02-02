import logging

from openai import AsyncOpenAI
from src.core.config import settings
from src.schemas.chat import HistorySchema, RequestSchema, ResponseSchema
from src.utils.connect_retry import retry_with_reconnect

logger = logging.getLogger(__name__)


class _OpenAIClient:
    def __init__(self) -> None:
        self.client: AsyncOpenAI | None = None

    async def connect(self) -> None:  # need to add retry and backoff
        if self.client is not None:
            return
        self.client = AsyncOpenAI(
            api_key=settings.MODEL_TOKEN, base_url=settings.PROXYAPI_BASE_URL,
        )

    @retry_with_reconnect
    async def embedding(
        self, text: str, model: str = settings.EMBEDDING_MODEL,
    ) -> list[float] | None:

        text = text.strip()
        if not text:
            return None

        try:
            response = await self.client.embeddings.create(
                input=text, model=model,
            )
            return response.data[0].embedding
        
        except Exception:
            logger.exception("OpenAI embedding error")
            return None

    @retry_with_reconnect
    async def generate(
        self, request: RequestSchema, history: HistorySchema,
    ) -> ResponseSchema:
        
        try:
            messages = [
                message.model_dump(exclude_none=True)
                for message in history.messages
            ]
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
                tokens_used=resp.usage.total_tokens if resp.usage else None,
            )
        
        except Exception:
            logger.exception("OpenAI generate error")
            raise


_openai_client = _OpenAIClient()


def get_openai_client() -> _OpenAIClient:
    return _openai_client
