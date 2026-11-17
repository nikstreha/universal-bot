from typing import ClassVar

from universal_bot.domain.enum.exception.category import ErrorCategory
from universal_bot.domain.exception.base import DomainError


class AccessRequestAlreadyDecidedError(DomainError):
    code: ClassVar[str] = "ALREADY_DECIDED"
    category: ClassVar[ErrorCategory] = ErrorCategory.CONFLICT
    message_template: ClassVar[str] = "По запросу уже принято решение"
