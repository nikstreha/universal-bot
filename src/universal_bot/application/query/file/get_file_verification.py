from universal_bot.application.port.persistence.repository.verification.reader import (
    IVerificationReader,
)
from universal_bot.application.query.file.get_file import GetFileInteractor
from universal_bot.application.query_model.verification import VerificationQueryModel
from universal_bot.domain.common.guard import ensure
from universal_bot.domain.exception.common import NotFoundError
from universal_bot.domain.value_object.verification.id import VerificationId


class GetFileVerificationInteractor:
    def __init__(
        self, *, get_file: GetFileInteractor, verification_reader: IVerificationReader
    ) -> None:
        self._get_file = get_file
        self._verification_reader = verification_reader

    async def __call__(
        self, *, user_id: int, file_id: str, verification_id: str
    ) -> VerificationQueryModel:
        await self._get_file(user_id=user_id, file_id=file_id)
        row = await self._verification_reader.find_by_id(
            key=VerificationId(verification_id)
        )
        ensure(row and row.file_id == file_id, NotFoundError, "Проверка не найдена")
        return row
