from dishka import Provider, Scope, provide

from universal_bot.application.query.upload.get_upload import GetUploadInteractor
from universal_bot.application.query.upload.get_upload_part_size import (
    GetUploadPartSizeInteractor,
)


class UploadQueryProvider(Provider):
    scope = Scope.REQUEST
    get_upload_interactor = provide(GetUploadInteractor)
    get_upload_part_size_interactor = provide(GetUploadPartSizeInteractor)
