from dishka import Provider, Scope, provide

from universal_bot.application.query.file.get_file import GetFileInteractor
from universal_bot.application.query.file.get_file_catalog import (
    GetFileCatalogInteractor,
)
from universal_bot.application.query.file.get_file_date_list import (
    GetFileDateListInteractor,
)
from universal_bot.application.query.file.get_file_verification import (
    GetFileVerificationInteractor,
)


class FileQueryProvider(Provider):
    scope = Scope.REQUEST
    get_file_interactor = provide(GetFileInteractor)
    get_file_catalog_interactor = provide(GetFileCatalogInteractor)
    get_file_date_list_interactor = provide(GetFileDateListInteractor)
    get_file_verification_interactor = provide(GetFileVerificationInteractor)
