from enum import StrEnum


class AdminButtons(StrEnum):
    BAN_USER = "Ban user"
    CHANGE_ROLE = "Change role"
    ADD_USER = "Add user"
    USER_LIST = "User list"
    LOOKUP_USER = "Find user"
    MESSAGE_FOR_ADMIN = "Messages for admin"
    EXIT = "Exit admin panel"


class ActionButtons(StrEnum):
    CANCEL = "Cancel"
    NEXT = "Next page"
    CONFIRM = "✓ Confirm"
