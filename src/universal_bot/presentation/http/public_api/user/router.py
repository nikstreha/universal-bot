from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends

from universal_bot.application.query.user.get_profile import GetProfileInteractor
from universal_bot.application.query_model.session import SessionQueryModel
from universal_bot.presentation.http.public_api.auth.dependencies import session
from universal_bot.presentation.http.public_api.user.schema import UserResponse


def create_user_router() -> APIRouter:
    router = APIRouter(prefix="", tags=["user"])

    @router.get("/me")
    @inject
    async def me(
        current: SessionQueryModel = Depends(session),
        *,
        get_profile: FromDishka[GetProfileInteractor],
    ) -> UserResponse:
        return UserResponse.model_validate(await get_profile(user_id=current.user_id))

    return router
