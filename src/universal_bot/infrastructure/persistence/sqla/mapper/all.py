from universal_bot.infrastructure.persistence.sqla.mapper.access_request import (
    map_access_request_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.admin_dialog import (
    map_admin_dialog_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.admin_notification import (
    map_admin_notification_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.administrator import (
    map_administrator_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.audit_event import (
    map_audit_event_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.auth_attempt import (
    map_auth_attempt_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.delivery import (
    map_delivery_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.file import map_file_table
from universal_bot.infrastructure.persistence.sqla.mapper.job import map_job_table
from universal_bot.infrastructure.persistence.sqla.mapper.rate_limit import (
    map_rate_limit_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.service_state import (
    map_service_state_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.session import (
    map_session_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.telegram_update import (
    map_telegram_update_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.transcription import (
    map_transcription_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.upload import map_upload_table
from universal_bot.infrastructure.persistence.sqla.mapper.upload_part import (
    map_upload_part_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.user import map_user_table
from universal_bot.infrastructure.persistence.sqla.mapper.verification import (
    map_verification_table,
)
from universal_bot.infrastructure.persistence.sqla.mapper.whitelist import (
    map_whitelist_table,
)

_configured = False


def map_tables() -> None:
    global _configured
    if _configured:
        return
    map_user_table()
    map_administrator_table()
    map_whitelist_table()
    map_session_table()
    map_auth_attempt_table()
    map_access_request_table()
    map_admin_notification_table()
    map_audit_event_table()
    map_upload_table()
    map_upload_part_table()
    map_file_table()
    map_verification_table()
    map_job_table()
    map_admin_dialog_table()
    map_telegram_update_table()
    map_transcription_table()
    map_delivery_table()
    map_rate_limit_table()
    map_service_state_table()
    _configured = True
    return
