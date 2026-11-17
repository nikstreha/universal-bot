from dataclasses import dataclass

from universal_bot.domain.exception.access import AdminConfigurationMismatchError
from universal_bot.domain.value_object.common import ValueObject


@dataclass(frozen=True, slots=True, repr=False)
class AdministratorId(ValueObject):
    value: int = 1

    def __post_init__(self) -> None:
        if type(self.value) is not int or self.value != 1:
            raise AdminConfigurationMismatchError(
                "В системе может быть только один администратор"
            )
