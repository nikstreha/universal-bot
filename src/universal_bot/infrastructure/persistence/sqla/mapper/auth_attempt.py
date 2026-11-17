from sqlalchemy.orm import composite

from universal_bot.domain.entity.login_attempt import LoginAttempt
from universal_bot.domain.enum.login_attempt.status import LoginAttemptStatus
from universal_bot.domain.value_object.auth.code_challenge import CodeChallenge
from universal_bot.domain.value_object.auth.device_name import DeviceName
from universal_bot.domain.value_object.auth.installation_id import InstallationId
from universal_bot.domain.value_object.auth.login_code import LoginCode
from universal_bot.domain.value_object.login_attempt.id import LoginAttemptId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.auth_attempt import (
    auth_attempt_table,
)
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_auth_attempt_table() -> None:
    auth_attempt_table.c.status.type = EnumStringType(LoginAttemptStatus)
    mapping_registry.map_imperatively(
        LoginAttempt,
        auth_attempt_table,
        properties={
            "_id": composite(LoginAttemptId, auth_attempt_table.c.id),
            "challenge": composite(CodeChallenge, auth_attempt_table.c.challenge),
            "login_code": composite(LoginCode, auth_attempt_table.c.login_code),
            "installation_id": composite(
                InstallationId, auth_attempt_table.c.installation_id
            ),
            "device_name": composite(DeviceName, auth_attempt_table.c.device_name),
            "expires_at": composite(Timestamp, auth_attempt_table.c.expires_at),
            "_status": auth_attempt_table.c.status,
            "candidate_id": composite(
                TelegramUserId.from_raw, auth_attempt_table.c.candidate_id
            ),
            "user_id": composite(TelegramUserId.from_raw, auth_attempt_table.c.user_id),
            "consumed_at": composite(
                Timestamp.from_raw, auth_attempt_table.c.consumed_at
            ),
        },
        column_prefix="_raw_",
    )
