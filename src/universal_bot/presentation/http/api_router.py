from fastapi import APIRouter

from universal_bot.presentation.http.public_api.access_request.router import (
    create_access_request_router,
)
from universal_bot.presentation.http.public_api.auth.router import (
    create_auth_router,
)
from universal_bot.presentation.http.public_api.file.router import (
    create_file_router,
)
from universal_bot.presentation.http.public_api.session.router import (
    create_session_router,
)
from universal_bot.presentation.http.public_api.upload.router import (
    create_upload_router,
)
from universal_bot.presentation.http.public_api.user.router import (
    create_user_router,
)


def create_api_router() -> APIRouter:
    router = APIRouter(prefix="/api/v1")
    router.include_router(create_auth_router())
    router.include_router(create_session_router())
    router.include_router(create_access_request_router())
    router.include_router(create_file_router())
    router.include_router(create_upload_router())
    router.include_router(create_user_router())
    return router
