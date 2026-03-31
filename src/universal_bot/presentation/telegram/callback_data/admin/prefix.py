from enum import StrEnum


class AdminCallbackPrefix(StrEnum):
    ADMIN = "adm"
    ADD_USER = "add_usr"
    CHANGE_ROLE = "chng_r"
    BAN_USER = "ban_usr"
    MESSAGE = "msg"
    USER = "usr"


class PrefixCallback(StrEnum):
    PAGINATION = "pagination"

    ADMIN_MESSAGES = "adm_msg"

    USER_LIST = "usr_lst"

    BAN = "ban"
    CHANGE_ROLE = "change_role"

    CANCEL = "admin:cancel"

    ADD_ROLE = "add_role"
    SET_ROLE = "set_role"

    BAN_PROMPT = "ban_prompt"
    ROLE_PROMPT = "role_prompt"
