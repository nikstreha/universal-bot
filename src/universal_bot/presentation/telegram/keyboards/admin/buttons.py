from enum import StrEnum


class AdminButtons(StrEnum):
    BAN_USER = "Ban user"
    CHANGE_ROLE = "Change role"
    ADD_USER = "Add user"
    USER_LIST = "User list"
    LOOKUP_USER = "Find user"
    EXIT = "Exit admin panel"
