import asyncio
import logging

from dishka import AsyncContainer

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
from universal_bot.domain.entity.job import Job
from universal_bot.domain.exception.base import BaseError

logger = logging.getLogger(__name__)
JOB_HANDLERS = {
    "finalize": FinalizeUploadInteractor,
    "thumbnail": CreateThumbnailInteractor,
    "verify": VerifyFileInteractor,
    "transcribe": TranscribeAudioInteractor,
}


class JobWorker:
    def __init__(self, container: AsyncContainer) -> None:
        self._container = container

    async def _heartbeat(self, job: Job) -> None:
        while True:
            await asyncio.sleep(20)
            async with self._container() as scope:
                renew = await scope.get(RenewJobLeaseInteractor)
                await renew(job=job)

    async def _execute(self, job: Job) -> None:
        heartbeat = asyncio.create_task(self._heartbeat(job))
        error = None
        try:
            async with self._container() as scope:
                handler = await scope.get(JOB_HANDLERS[job.kind])
                await handler(job=job)
        except Exception as exc:
            error = exc
            logger.log(
                logging.WARNING if isinstance(exc, BaseError) else logging.ERROR,
                "Job %s %s failed: %s",
                str(job.id_.value),
                job.kind,
                getattr(exc, "code", type(exc).__name__),
                exc_info=exc,
                extra={
                    "event": "job_failed",
                    "job_id": str(job.id_.value),
                    "job_kind": str(job.kind),
                    "error_code": getattr(exc, "code", type(exc).__name__),
                },
            )
        finally:
            heartbeat.cancel()
            await asyncio.gather(heartbeat, return_exceptions=True)
        async with self._container() as scope:
            finish = await scope.get(FinishJobInteractor)
            await finish(job=job, error=error)
        if error is None:
            logger.info(
                "Job completed",
                extra={
                    "event": "job_completed",
                    "job_id": str(job.id_.value),
                    "job_kind": str(job.kind),
                },
            )

    async def _lane(self, kinds: tuple[str, ...]) -> None:
        while True:
            try:
                async with self._container() as scope:
                    claim = await scope.get(ClaimJobInteractor)
                    job = await claim(kinds=kinds)
                if job:
                    await self._execute(job)
                else:
                    await asyncio.sleep(1)
            except BaseError as exc:
                logger.info("Worker operation deferred: %s", exc.code)
                await asyncio.sleep(1)
            except Exception as exc:
                logger.error(
                    "Worker operation deferred: %s",
                    type(exc).__name__,
                    exc_info=exc,
                    extra={"event": "worker_failed"},
                )
                await asyncio.sleep(5)

    async def _maintenance(self) -> None:
        while True:
            try:
                async with self._container() as scope:
                    maintain = await scope.get(MaintainStorageInteractor)
                    await maintain()
            except Exception as exc:
                logger.error(
                    "Storage maintenance deferred: %s",
                    type(exc).__name__,
                    exc_info=exc,
                    extra={"event": "storage_maintenance_failed"},
                )
            await asyncio.sleep(30)

    async def run(self) -> None:
        async with asyncio.TaskGroup() as tasks:
            tasks.create_task(self._lane(("finalize", "verify", "thumbnail")))
            tasks.create_task(self._lane(("transcribe",)))
            tasks.create_task(self._maintenance())
