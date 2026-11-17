from dishka import Provider, Scope, provide

from universal_bot.application.command.file.request_file_verification import (
    RequestFileVerificationInteractor,
)
from universal_bot.application.command.file.restore_file import RestoreFileInteractor
from universal_bot.application.command.file.trash_file import TrashFileInteractor


class FileCommandProvider(Provider):
    scope = Scope.REQUEST
    trash_file_interactor = provide(TrashFileInteractor)
    restore_file_interactor = provide(RestoreFileInteractor)
    request_file_verification_interactor = provide(RequestFileVerificationInteractor)
