from dishka import Provider, Scope, provide

from universal_bot.presentation.http.public_api.file.response import FileResponseFactory
from universal_bot.presentation.telegram.handler.admin import TelegramAdminHandler
from universal_bot.presentation.telegram.handler.update import TelegramUpdateHandler


class PresentationProvider(Provider):
    scope = Scope.REQUEST
    file_response = provide(FileResponseFactory)
    telegram_handler = provide(TelegramUpdateHandler)

    telegram_admin_handler = provide(TelegramAdminHandler)
