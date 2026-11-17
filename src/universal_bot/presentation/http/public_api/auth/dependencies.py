from hashlib import sha256

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import Header, Request

from universal_bot.application.command.access.apply_rate_limit import (
    ApplyRateLimitInteractor,
)
from universal_bot.application.command.auth.authenticate_session import (
    AuthenticateSessionInteractor,
)
from universal_bot.application.exception.common import AuthRequiredError
from universal_bot.application.query_model.session import SessionQueryModel
from universal_bot.domain.common.guard import ensure


@inject
async def session(
    authorization: str = Header(default=""),
    *,
    authenticate_session: FromDishka[AuthenticateSessionInteractor],
) -> SessionQueryModel:
    ensure(
        authorization.startswith("Bearer "), AuthRequiredError, "Войдите через Telegram"
    )
    return await authenticate_session(secret=authorization[7:])


@inject
async def auth_budget(
    request: Request, *, apply_rate_limit: FromDishka[ApplyRateLimitInteractor]
) -> None:
    peer = request.client.host if request.client else "unknown"
    key = sha256(peer.encode()).hexdigest()
    await apply_rate_limit(key="auth:global", maximum=600)
    await apply_rate_limit(key="auth:peer:" + key, maximum=120)
