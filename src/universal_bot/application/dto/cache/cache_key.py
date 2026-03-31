from enum import StrEnum


class CacheKey(StrEnum):
    USER_PERMISSION = "user_permission"
    USER_LIST = "user_list"
    MESSAGES_FOR_ADMIN = "messages_for_admin"
