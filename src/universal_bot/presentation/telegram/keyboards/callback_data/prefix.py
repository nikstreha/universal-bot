from enum import StrEnum


class CallbackMainPrefix(StrEnum):
    ADMIN = "admin"


class PrefixCallback(StrEnum):
    ADMIN_MESSAGES = "adm_msg"
    USER_LIST = "usr_lst"
    BAN = "ban"
    CANCEL = "cancel"
    CHANGE_ROLE = "change_role"
    ADD_ROLE = "add_role"
    SET_ROLE = "set_role"
    BAN_PROMPT = "ban_prompt"
    ROLE_PROMPT = "role_prompt"
