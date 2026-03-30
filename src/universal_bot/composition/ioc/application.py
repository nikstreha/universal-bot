from dishka import Provider, Scope, provide

from universal_bot.application.command.admin.add_user import AddUserInteractor
from universal_bot.application.command.admin.ban import BanUserInteractor
from universal_bot.application.command.admin.update_role import UpdateRoleInteractor
from universal_bot.application.port.cache.cache_provider import ICacheProvider
from universal_bot.application.port.db.repositories.user.reader import IUserReader
from universal_bot.application.port.db.repositories.user.writer import IUserWriter
from universal_bot.application.query.admin.get_user import GetUserInteractor
from universal_bot.application.query.admin.user_list import GetUserListInteractor


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


class QueryProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_user_list_query(
        self, user_reader: IUserReader, cache_provider: ICacheProvider
    ) -> GetUserListInteractor:
        return GetUserListInteractor(
            user_reader=user_reader,
            cache=cache_provider,
        )

    @provide
    def get_user_query(self, user_reader: IUserReader) -> GetUserInteractor:
        return GetUserInteractor(user_reader=user_reader)


def _application_provider() -> tuple[Provider, ...]:
    return (
        QueryProvider(),
        CommandProvider(),
    )
