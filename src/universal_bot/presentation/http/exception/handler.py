import logging

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from universal_bot.domain.exception.base import BaseError
from universal_bot.domain.exception.common import InvalidRequestError
from universal_bot.presentation.http.exception.catalog import ErrorCatalog
from universal_bot.presentation.http.exception.schema import (
    ErrorResponse,
    ProblemResponse,
)


async def problem(request: Request, exc: BaseError) -> JSONResponse:
    status = ErrorCatalog.status_for(exc)
    if status in (401, 403):
        logging.getLogger(__name__).warning(
            "HTTP access denied",
            extra={
                "event": "access_denied",
                "status": status,
                "request_id": request.state.request_id,
                "error_code": exc.code,
            },
        )
    headers = (
        {"Retry-After": str(exc.details.get("retry_after", 5))}
        if status in (429, 503)
        else {}
    )
    body = ProblemResponse(
        error=ErrorResponse(
            code=exc.code,
            message=exc.public_message,
            retryable=status in (429, 503, 507),
            details=exc.public_payload,
        ),
        request_id=request.state.request_id,
    )
    return JSONResponse(
        body.model_dump(mode="json"), status_code=status, headers=headers
    )


async def invalid(request: Request, exc: RequestValidationError) -> JSONResponse:
    return await problem(request, InvalidRequestError("Проверьте параметры запроса"))


async def unexpected(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger(__name__).error(
        "Unhandled HTTP error",
        exc_info=exc,
        extra={"event": "http_unhandled_error", "request_id": request.state.request_id},
    )
    return await problem(request, BaseError())
