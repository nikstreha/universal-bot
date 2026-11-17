from sqlalchemy.orm import composite

from universal_bot.domain.entity.access_dialog import AccessDialog
from universal_bot.domain.enum.admin_dialog.action import AdminDialogAction
from universal_bot.domain.value_object.time.timestamp import Timestamp
from universal_bot.domain.value_object.user.id import TelegramUserId
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry
from universal_bot.infrastructure.persistence.sqla.table.admin_dialog import (
    admin_dialog_table,
)
from universal_bot.infrastructure.persistence.sqla.type import EnumStringType


def map_admin_dialog_table() -> None:
    admin_dialog_table.c.action.type = EnumStringType(AdminDialogAction)
    mapping_registry.map_imperatively(
        AccessDialog,
        admin_dialog_table,
        properties={
            "_id": composite(TelegramUserId, admin_dialog_table.c.admin_id),
            "action": admin_dialog_table.c.action,
            "expires_at": composite(Timestamp, admin_dialog_table.c.expires_at),
            "payload": admin_dialog_table.c.payload,
        },
        column_prefix="_raw_",
    )
