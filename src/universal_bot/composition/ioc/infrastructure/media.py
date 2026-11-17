from dishka import Provider, Scope, provide

from universal_bot.application.port.media.inspector import IMediaInspector
from universal_bot.application.port.media.thumbnailer import IThumbnailer
from universal_bot.application.port.persistence.file_storage.object_storage import (
    IObjectStorage,
)
from universal_bot.composition.configuration.media_configuration import (
    MediaConfiguration,
)
from universal_bot.infrastructure.media.processing import (
    FiletypeInspector,
    LocalThumbnailer,
)


class MediaProvider(Provider):
    inspector = provide(FiletypeInspector, provides=IMediaInspector, scope=Scope.APP)

    @provide(scope=Scope.APP)
    def thumbnailer(
        self, storage: IObjectStorage, config: MediaConfiguration
    ) -> IThumbnailer:
        return LocalThumbnailer(storage, config.temporary_directory)
