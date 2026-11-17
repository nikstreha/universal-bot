from hashlib import sha256
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Request, Response

from universal_bot.application.command.access.apply_rate_limit import (
    ApplyRateLimitInteractor,
)
from universal_bot.application.command.auth.create_login_attempt import (
    CreateLoginAttemptInteractor,
)
from universal_bot.application.command.auth.exchange_login_attempt import (
    ExchangeLoginAttemptInteractor,
)
from universal_bot.application.command.auth.revoke_session import (
    RevokeSessionInteractor,
)
from universal_bot.application.query_model.login import PendingLoginQueryModel
from universal_bot.application.query_model.session import SessionQueryModel
from universal_bot.presentation.http.public_api.auth.dependencies import (
    auth_budget,
    session,
)
from universal_bot.presentation.http.public_api.auth.schema import (
    AttemptBody,
    AuthenticatedSessionResponse,
    LoginAttemptResponse,
    PendingLoginResponse,
    ProofBody,
)


def create_auth_router() -> APIRouter:
    router = APIRouter(prefix="/auth", tags=["auth"])

    @router.post(
        "/telegram/attempts", status_code=201, dependencies=[Depends(auth_budget)]
    )
    @inject
    async def attempt(
        body: AttemptBody,
        request: Request,
        *,
        apply_rate_limit: FromDishka[ApplyRateLimitInteractor],
        create_login_attempt: FromDishka[CreateLoginAttemptInteractor],
    ) -> LoginAttemptResponse:
        await apply_rate_limit(
            key="login:"
            + sha256(
                (request.client.host if request.client else "unknown").encode()
            ).hexdigest(),
            maximum=20,
        )
        result = await create_login_attempt(
            challenge=body.code_challenge,
            installation_id=body.installation_id,
            device_name=body.device_name,
        )
        return LoginAttemptResponse.model_validate(result)

    @router.post(
        "/telegram/attempts/{attempt_id}/exchange", dependencies=[Depends(auth_budget)]
    )
    @inject
    async def exchange(
        attempt_id: UUID,
        body: ProofBody,
        response: Response,
        *,
        exchange_login_attempt: FromDishka[ExchangeLoginAttemptInteractor],
    ) -> PendingLoginResponse | AuthenticatedSessionResponse:
        result = await exchange_login_attempt(
            attempt_id=str(attempt_id), verifier=body.code_verifier
        )
        if isinstance(result, PendingLoginQueryModel):
            response.status_code = 202
            return PendingLoginResponse()
        return AuthenticatedSessionResponse.model_validate(result)

    @router.post("/logout", status_code=204)
    @inject
    async def logout(
        current: SessionQueryModel = Depends(session),
        *,
        revoke_session: FromDishka[RevokeSessionInteractor],
    ) -> None:
        await revoke_session(user_id=current.user_id, session_id=current.id)

    return router
