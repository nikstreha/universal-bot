from collections.abc import AsyncIterator
from typing import cast

from dishka import Provider, Scope, alias, provide
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from universal_bot.application.port.persistence.repository.access_dialog.writer import (
    IAccessDialogWriter,
)
from universal_bot.application.port.persistence.repository.access_grant.reader import (
    IAccessGrantReader,
)
from universal_bot.application.port.persistence.repository.access_grant.writer import (
    IAccessGrantWriter,
)
from universal_bot.application.port.persistence.repository.access_request.reader import (
    IAccessRequestReader,
)
from universal_bot.application.port.persistence.repository.access_request.writer import (
    IAccessRequestWriter,
)
from universal_bot.application.port.persistence.repository.admin_notification.reader import (
    IAdminNotificationReader,
)
from universal_bot.application.port.persistence.repository.admin_notification.writer import (
    IAdminNotificationWriter,
)
from universal_bot.application.port.persistence.repository.administrator.reader import (
    IAdministratorReader,
)
from universal_bot.application.port.persistence.repository.administrator.writer import (
    IAdministratorWriter,
)
from universal_bot.application.port.persistence.repository.audit_event.writer import (
    IAuditEventWriter,
)
from universal_bot.application.port.persistence.repository.delivery.writer import (
    IDeliveryWriter,
)
from universal_bot.application.port.persistence.repository.job.writer import IJobWriter
from universal_bot.application.port.persistence.repository.login_attempt.writer import (
    ILoginAttemptWriter,
)
from universal_bot.application.port.persistence.repository.rate_limit.writer import (
    IRateLimitWriter,
)
from universal_bot.application.port.persistence.repository.service_state.reader import (
    IServiceStateReader,
)
from universal_bot.application.port.persistence.repository.service_state.writer import (
    IServiceStateWriter,
)
from universal_bot.application.port.persistence.repository.session.reader import (
    ISessionReader,
)
from universal_bot.application.port.persistence.repository.session.writer import (
    ISessionWriter,
)
from universal_bot.application.port.persistence.repository.stored_file.reader import (
    IStoredFileReader,
)
from universal_bot.application.port.persistence.repository.stored_file.writer import (
    IStoredFileWriter,
)
from universal_bot.application.port.persistence.repository.telegram_update.reader import (
    ITelegramUpdateReader,
)
from universal_bot.application.port.persistence.repository.telegram_update.writer import (
    ITelegramUpdateWriter,
)
from universal_bot.application.port.persistence.repository.transcription.writer import (
    ITranscriptionWriter,
)
from universal_bot.application.port.persistence.repository.upload.reader import (
    IUploadReader,
)
from universal_bot.application.port.persistence.repository.upload.writer import (
    IUploadWriter,
)
from universal_bot.application.port.persistence.repository.upload_part.reader import (
    IUploadPartReader,
)
from universal_bot.application.port.persistence.repository.upload_part.writer import (
    IUploadPartWriter,
)
from universal_bot.application.port.persistence.repository.user.reader import (
    IUserReader,
)
from universal_bot.application.port.persistence.repository.user.writer import (
    IUserWriter,
)
from universal_bot.application.port.persistence.repository.verification.reader import (
    IVerificationReader,
)
from universal_bot.application.port.persistence.repository.verification.writer import (
    IVerificationWriter,
)
from universal_bot.application.port.persistence.uow import IUnitOfWork
from universal_bot.composition.configuration.persistence_configuration import (
    PersistenceConfiguration,
)
from universal_bot.infrastructure.persistence.sqla.mapper.all import map_tables
from universal_bot.infrastructure.persistence.sqla.repository.access_dialog.writer import (
    SQLAAccessDialogWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.access_grant.reader import (
    SQLAAccessGrantReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.access_grant.writer import (
    SQLAAccessGrantWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.access_request.reader import (
    SQLAAccessRequestReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.access_request.writer import (
    SQLAAccessRequestWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.admin_notification.reader import (
    SQLAAdminNotificationReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.admin_notification.writer import (
    SQLAAdminNotificationWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.administrator.reader import (
    SQLAAdministratorReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.administrator.writer import (
    SQLAAdministratorWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.audit_event.writer import (
    SQLAAuditEventWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.delivery.writer import (
    SQLADeliveryWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.job.writer import (
    SQLAJobWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.login_attempt.writer import (
    SQLALoginAttemptWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.rate_limit.writer import (
    SQLARateLimitWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.service_state.reader import (
    SQLAServiceStateReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.service_state.writer import (
    SQLAServiceStateWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.session.reader import (
    SQLASessionReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.session.writer import (
    SQLASessionWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.stored_file.reader import (
    SQLAStoredFileReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.stored_file.writer import (
    SQLAStoredFileWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.telegram_update.reader import (
    SQLATelegramUpdateReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.telegram_update.writer import (
    SQLATelegramUpdateWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.transcription.writer import (
    SQLATranscriptionWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.upload.reader import (
    SQLAUploadReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.upload.writer import (
    SQLAUploadWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.upload_part.reader import (
    SQLAUploadPartReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.upload_part.writer import (
    SQLAUploadPartWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.user.reader import (
    SQLAUserReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.user.writer import (
    SQLAUserWriter,
)
from universal_bot.infrastructure.persistence.sqla.repository.verification.reader import (
    SQLAVerificationReader,
)
from universal_bot.infrastructure.persistence.sqla.repository.verification.writer import (
    SQLAVerificationWriter,
)
from universal_bot.infrastructure.persistence.sqla.session_proxy import SessionProxy
from universal_bot.infrastructure.persistence.sqla.sqla_persistence_connector import (
    SQLAPersistenceConnector,
)
from universal_bot.infrastructure.persistence.sqla.sqla_uow import SQLAUnitOfWork
from universal_bot.infrastructure.persistence.sqla.type import (
    ReaderSession,
    WriterSession,
)


class PersistenceProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    async def connector(
        self, config: PersistenceConfiguration
    ) -> AsyncIterator[SQLAPersistenceConnector]:
        map_tables()
        connector = SQLAPersistenceConnector(config.database_path)
        try:
            await connector.connect()
            yield connector
        finally:
            await connector.disconnect()

    @provide(scope=Scope.APP)
    def session_factory(
        self, connector: SQLAPersistenceConnector
    ) -> async_sessionmaker[AsyncSession]:
        return connector.session_factory

    uow = provide(SQLAUnitOfWork, scope=Scope.REQUEST)
    abstract_uow = alias(SQLAUnitOfWork, provides=IUnitOfWork)

    @provide(scope=Scope.REQUEST)
    async def reader_session(
        self, factory: async_sessionmaker[AsyncSession]
    ) -> AsyncIterator[ReaderSession]:
        async with factory() as session:
            yield ReaderSession(session)

    @provide(scope=Scope.REQUEST)
    def writer_session(self, uow: SQLAUnitOfWork) -> WriterSession:
        return cast(WriterSession, SessionProxy(uow))

    access_grant_reader = provide(SQLAAccessGrantReader, provides=IAccessGrantReader)
    access_request_reader = provide(
        SQLAAccessRequestReader, provides=IAccessRequestReader
    )
    admin_notification_reader = provide(
        SQLAAdminNotificationReader, provides=IAdminNotificationReader
    )
    service_state_reader = provide(SQLAServiceStateReader, provides=IServiceStateReader)
    session_reader = provide(SQLASessionReader, provides=ISessionReader)
    stored_file_reader = provide(SQLAStoredFileReader, provides=IStoredFileReader)
    telegram_update_reader = provide(
        SQLATelegramUpdateReader, provides=ITelegramUpdateReader
    )
    upload_reader = provide(SQLAUploadReader, provides=IUploadReader)
    upload_part_reader = provide(SQLAUploadPartReader, provides=IUploadPartReader)
    user_reader = provide(SQLAUserReader, provides=IUserReader)
    verification_reader = provide(SQLAVerificationReader, provides=IVerificationReader)
    access_dialog_writer = provide(SQLAAccessDialogWriter, provides=IAccessDialogWriter)
    access_grant_writer = provide(SQLAAccessGrantWriter, provides=IAccessGrantWriter)
    access_request_writer = provide(
        SQLAAccessRequestWriter, provides=IAccessRequestWriter
    )
    admin_notification_writer = provide(
        SQLAAdminNotificationWriter, provides=IAdminNotificationWriter
    )
    audit_event_writer = provide(SQLAAuditEventWriter, provides=IAuditEventWriter)
    delivery_writer = provide(SQLADeliveryWriter, provides=IDeliveryWriter)
    job_writer = provide(SQLAJobWriter, provides=IJobWriter)
    login_attempt_writer = provide(SQLALoginAttemptWriter, provides=ILoginAttemptWriter)
    rate_limit_writer = provide(SQLARateLimitWriter, provides=IRateLimitWriter)
    service_state_writer = provide(SQLAServiceStateWriter, provides=IServiceStateWriter)
    session_writer = provide(SQLASessionWriter, provides=ISessionWriter)
    stored_file_writer = provide(SQLAStoredFileWriter, provides=IStoredFileWriter)
    telegram_update_writer = provide(
        SQLATelegramUpdateWriter, provides=ITelegramUpdateWriter
    )
    transcription_writer = provide(
        SQLATranscriptionWriter, provides=ITranscriptionWriter
    )
    upload_writer = provide(SQLAUploadWriter, provides=IUploadWriter)
    upload_part_writer = provide(SQLAUploadPartWriter, provides=IUploadPartWriter)
    user_writer = provide(SQLAUserWriter, provides=IUserWriter)
    verification_writer = provide(SQLAVerificationWriter, provides=IVerificationWriter)

    administrator_reader = provide(
        SQLAAdministratorReader, provides=IAdministratorReader
    )
    administrator_writer = provide(
        SQLAAdministratorWriter, provides=IAdministratorWriter
    )
