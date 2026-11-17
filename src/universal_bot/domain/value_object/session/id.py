from dataclasses import dataclass

from universal_bot.domain.value_object.identifier import UUIDIdentifier


@dataclass(frozen=True, slots=True, repr=False)
class SessionId(UUIDIdentifier):
    pass
