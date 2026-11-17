from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, Response

from universal_bot.application.command.access.request_access import (
    RequestAccessInteractor,
)
from universal_bot.application.query.auth.get_denied_login_identity import (
    GetDeniedLoginIdentityInteractor,
)
from universal_bot.application.query.telegram.get_access_request_status import (
    GetAccessRequestStatusInteractor,
)
from universal_bot.presentation.http.public_api.access_request.schema import (
    AccessBody,
    AccessRequestResponse,
    AccessRequestStatusResponse,
)
from universal_bot.presentation.http.public_api.auth.dependencies import auth_budget


def create_access_request_router() -> APIRouter:
    router = APIRouter(prefix="/access-requests", tags=["access_request"])

    @router.post("", dependencies=[Depends(auth_budget)])
    @inject
    async def access_request(
        body: AccessBody,
        response: Response,
        *,
        get_denied_login_identity: FromDishka[GetDeniedLoginIdentityInteractor],
        request_access: FromDishka[RequestAccessInteractor],
    ) -> AccessRequestResponse:
        user_id = await get_denied_login_identity(
            attempt_id=str(body.attempt_id), verifier=body.code_verifier
        )
        row, created = await request_access(user_id=user_id, source="app")
        response.status_code = 201 if created else 200
        return AccessRequestResponse.model_validate(
            {**row.to_dict(), "can_request_access": False}
        )

    @router.post("/status", dependencies=[Depends(auth_budget)])
    @inject
    async def access_status(
        body: AccessBody,
        *,
        get_access_request_status: FromDishka[GetAccessRequestStatusInteractor],
        get_denied_login_identity: FromDishka[GetDeniedLoginIdentityInteractor],
    ) -> AccessRequestStatusResponse:
        user_id = await get_denied_login_identity(
            attempt_id=str(body.attempt_id), verifier=body.code_verifier
        )
        status = await get_access_request_status(user_id=user_id)
        return AccessRequestStatusResponse(
            status=status, can_request_access=status == "not_requested"
        )

    return router
