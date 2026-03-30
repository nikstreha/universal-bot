from dishka import Provider, Scope, provide

from universal_bot.application.command.admin.add_user import AddUserInteractor
from universal_bot.application.command.admin.ban import BanUserInteractor
from universal_bot.application.command.admin.update_role import UpdateRoleInteractor
from universal_bot.application.command.common.unknown_user_message import (
    UnknownUserMessageInteractor,
)
from universal_bot.application.port.cache.cache_provider import ICacheProvider
from universal_bot.application.port.db.repositories.user.reader import IUserReader
from universal_bot.application.port.db.repositories.user.writer import IUserWriter
from universal_bot.application.query.admin.get_admin_messages import (
    GetAdminMessagesInteractor,
)
from universal_bot.application.query.admin.get_user import GetUserInteractor
from universal_bot.application.query.admin.user_list import GetUserListInteractor
from universal_bot.composition.configuration.config import Settings


class CommandProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_ban_user_command(self, user_writer: IUserWriter) -> BanUserInteractor:
        return BanUserInteractor(
            user_writer=user_writer,
        )

    @provide
    def get_update_user_role_command(
        self, user_writer: IUserWriter, cache_provider: ICacheProvider
    ) -> UpdateRoleInteractor:
        return UpdateRoleInteractor(
            user_writer=user_writer,
            cache_provider=cache_provider,
        )

    @provide
    def get_add_user_command(
        self, user_writer: IUserWriter, cache_provider: ICacheProvider
    ) -> AddUserInteractor:
        return AddUserInteractor(
            user_writer=user_writer,
            cache_provider=cache_provider,
        )

    @provide
    def get_unknown_user_message_command(
        self, cache_provider: ICacheProvider
    ) -> UnknownUserMessageInteractor:
        return UnknownUserMessageInteractor(
            cache_provider=cache_provider,
        )


class QueryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_user_list_query(
        self, user_reader: IUserReader, cache_provider: ICacheProvider
    ) -> GetUserListInteractor:
        return GetUserListInteractor(user_reader=user_reader)

    @provide
    def get_user_query(self, user_reader: IUserReader) -> GetUserInteractor:
        return GetUserInteractor(user_reader=user_reader)

    @provide
    def get_admin_messages_query(
        self, cache_provider: ICacheProvider, settings: Settings
    ) -> GetAdminMessagesInteractor:
        return GetAdminMessagesInteractor(
            cache_provider=cache_provider,
            page_size=settings.MESSAGE_FOR_ADMIN_PAGE_SIZE,
        )


def _application_provider() -> tuple[Provider, ...]:
    return (
        QueryProvider(),
        CommandProvider(),
    )
