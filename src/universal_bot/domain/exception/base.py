from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory


class BaseError(Exception):
    code: ClassVar[str] = "INTERNAL_ERROR"
    category: ClassVar[ErrorCategory] = ErrorCategory.INTERNAL
    message_template: ClassVar[str] = "Операция не выполнена"
    exposed_payload: ClassVar[frozenset[str]] = frozenset(
        {
            "retry_after",
            "attempt_id",
            "telegram_id",
            "access_request_status",
            "can_request_access",
            "file_id",
            "missing_parts",
            "telegram_code",
        }
    )

    def __init__(self, message: str | None = None, /, **payload: object) -> None:
        self.payload = payload
        self._message = message
        super().__init__(self.message)

    @property
    def message(self) -> str:
        return self._message if self._message is not None else self.message_template

    @property
    def details(self) -> dict[str, object]:
        return self.payload

    @property
    def public_message(self) -> str:
        return (
            "Внутренняя ошибка сервера"
            if self.category is ErrorCategory.INTERNAL
            else self.message
        )

    @property
    def public_payload(self) -> dict[str, object]:
        return {
            name: value
            for name, value in self.payload.items()
            if name in self.exposed_payload
        }


class DomainError(BaseError):
    category: ClassVar[ErrorCategory] = ErrorCategory.VALIDATION
