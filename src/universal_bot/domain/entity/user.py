from universal_bot.domain.entity.common import Entity
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.domain.value_object.user.name import UserName


class User(Entity[TelegramUserId]):
    _id: TelegramUserId
    name: UserName
    created_at: Timestamp
    last_seen_at: Timestamp

    def __init__(
        self,
        *,
        id_: TelegramUserId,
        name: UserName = UserName(""),
        created_at: Timestamp = Timestamp(0),
        last_seen_at: Timestamp = Timestamp(0),
    ) -> None:
        super().__init__(id_=id_)
        self.name = name
        self.created_at = created_at
        self.last_seen_at = last_seen_at

    def touch(self, name: UserName, at: Timestamp) -> None:
        if name.value:
            self.name = name
        self.last_seen_at = at
