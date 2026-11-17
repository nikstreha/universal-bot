from pydantic import BaseModel


class ErrorResponse(BaseModel):
    code: str
    message: str
    retryable: bool
    details: dict[str, object]


class ProblemResponse(BaseModel):
    error: ErrorResponse
    request_id: str
