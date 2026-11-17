from dishka import Provider, Scope, provide

from universal_bot.application.command.job.claim_job import ClaimJobInteractor
from universal_bot.application.command.job.create_thumbnail import (
    CreateThumbnailInteractor,
)
from universal_bot.application.command.job.finalize_upload import (
    FinalizeUploadInteractor,
)
from universal_bot.application.command.job.finish_job import FinishJobInteractor
from universal_bot.application.command.job.maintain_storage import (
    MaintainStorageInteractor,
)
from universal_bot.application.command.job.renew_job_lease import (
    RenewJobLeaseInteractor,
)
from universal_bot.application.command.job.transcribe_audio import (
    TranscribeAudioInteractor,
)
from universal_bot.application.command.job.verify_file import VerifyFileInteractor


class JobCommandProvider(Provider):
    scope = Scope.REQUEST
    claim_job_interactor = provide(ClaimJobInteractor)
    renew_job_lease_interactor = provide(RenewJobLeaseInteractor)
    finish_job_interactor = provide(FinishJobInteractor)
    finalize_upload_interactor = provide(FinalizeUploadInteractor)
    verify_file_interactor = provide(VerifyFileInteractor)
    create_thumbnail_interactor = provide(CreateThumbnailInteractor)
    maintain_storage_interactor = provide(MaintainStorageInteractor)
    transcribe_audio_interactor = provide(TranscribeAudioInteractor)
