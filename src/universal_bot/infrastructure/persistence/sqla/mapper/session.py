from sqlalchemy.orm import composite

from universal_bot.domain.entity.session import Session
from universal_bot.domain.value_object.auth.device_name import DeviceName
from universal_bot.domain.value_object.auth.installation_id import InstallationId
from universal_bot.domain.value_object.auth.token_hash import TokenHash
from universal_bot.domain.value_object.session.id import SessionId
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.session import session_table


def map_session_table() -> None:
    mapping_registry.map_imperatively(
        Session,
        session_table,
        properties={
            "_id": composite(SessionId, session_table.c.id),
            "user_id": composite(TelegramUserId, session_table.c.user_id),
            "token_hash": composite(TokenHash, session_table.c.token_hash),
            "installation_id": composite(
                InstallationId, session_table.c.installation_id
            ),
            "device_name": composite(DeviceName, session_table.c.device_name),
            "created_at": composite(Timestamp, session_table.c.created_at),
            "last_seen_at": composite(Timestamp, session_table.c.last_seen_at),
            "expires_at": composite(Timestamp, session_table.c.expires_at),
            "absolute_expires_at": composite(
                Timestamp, session_table.c.absolute_expires_at
            ),
            "revoked_at": composite(Timestamp.from_raw, session_table.c.revoked_at),
        },
        column_prefix="_raw_",
    )
