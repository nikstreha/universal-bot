from src.managers.base import BaseManager


class AdminManager(BaseManager):
    pass


def get_admin_manager() -> AdminManager:
    return AdminManager()
