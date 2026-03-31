from enum import StrEnum


class AdminActions(StrEnum):
    NEXT_MESSAGES = "next_msg"
    PREV_MESSAGES = "prev_msg"

    NEXT_USER_LIST = "next_usr_lst"
    PREV_USER_LIST = "prev_usr_lst"

    BAN_USER = "ban_usr"
    CONFIRM_BAN = "confirm_ban"

    ADD_ROLE = "add_r"
    SET_ROLE = "set_r"

    CHANGE_ROLE = "chng_r"
