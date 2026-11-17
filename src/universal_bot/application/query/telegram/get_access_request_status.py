from universal_bot.application.port.persistence.repository.access_request.reader import (
    IAccessRequestReader,
)
from universal_bot.domain.value_object.user.id import TelegramUserId


class GetAccessRequestStatusInteractor:
    def __init__(self, *, access_request_reader: IAccessRequestReader) -> None:
        self._access_request_reader = access_request_reader

    async def __call__(self, *, user_id: int) -> str:
        row = await self._access_request_reader.find_by_user_id(
            user_id=TelegramUserId(user_id)
        )
        return row.status if row else "not_requested"
