from dishka import Provider, Scope, provide

from universal_bot.application.command.upload.cancel_upload import (
    CancelUploadInteractor,
)
from universal_bot.application.command.upload.complete_upload import (
    CompleteUploadInteractor,
)
from universal_bot.application.command.upload.create_upload import (
    CreateUploadInteractor,
)
from universal_bot.application.command.upload.receive_upload_part import (
    ReceiveUploadPartInteractor,
)


class UploadCommandProvider(Provider):
    scope = Scope.REQUEST
    create_upload_interactor = provide(CreateUploadInteractor)
    receive_upload_part_interactor = provide(ReceiveUploadPartInteractor)
    complete_upload_interactor = provide(CompleteUploadInteractor)
    cancel_upload_interactor = provide(CancelUploadInteractor)
