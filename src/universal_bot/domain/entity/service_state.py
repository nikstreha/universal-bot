from universal_bot.domain.entity.common import Entity
from universal_bot.domain.value_object.service_state.key import ServiceStateKey


class ServiceState(Entity[ServiceStateKey]):
    _identity_field = "key"
    key: ServiceStateKey
    value: str

    def __init__(self, *, key: ServiceStateKey, value: str) -> None:
        super().__init__(id_=key)
        self.value = value

    @property
    def key(self) -> ServiceStateKey:
        return self.id_
