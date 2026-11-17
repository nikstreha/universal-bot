import logging
from collections.abc import Awaitable, Callable
from uuid import uuid4

from starlette.requests import Request
from starlette.responses import Response


async def metadata(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    request.state.request_id = str(uuid4())
    response = await call_next(request)
    if request.url.path != "/health/live":
        logging.getLogger(__name__).log(
            logging.ERROR if response.status_code >= 500 else logging.INFO,
            "HTTP request completed",
            extra={
                "event": "http_request",
                "request_id": request.state.request_id,
                "method": request.method,
                "route": getattr(request.scope.get("route"), "path", "<unmatched>"),
                "status": response.status_code,
            },
        )
    response.headers.update(
        {
            "X-Request-ID": request.state.request_id,
            "Cache-Control": "no-store",
            "X-Content-Type-Options": "nosniff",
        }
    )
    return response
