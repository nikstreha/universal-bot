from dishka import Provider, Scope, provide

from universal_bot.application.command.telegram.accept_audio import (
    AcceptAudioInteractor,
)
from universal_bot.application.command.telegram.authorize_delivery import (
    AuthorizeDeliveryInteractor,
)
from universal_bot.application.command.telegram.claim_delivery import (
    ClaimDeliveryInteractor,
)
from universal_bot.application.command.telegram.clear_telegram_dialog import (
    ClearTelegramDialogInteractor,
)
from universal_bot.application.command.telegram.complete_delivery import (
    CompleteDeliveryInteractor,
)
from universal_bot.application.command.telegram.complete_telegram_update import (
    CompleteTelegramUpdateInteractor,
)
from universal_bot.application.command.telegram.receive_telegram_updates import (
    ReceiveTelegramUpdatesInteractor,
)
from universal_bot.application.command.telegram.telegram_dialog import (
    TelegramDialogInteractor,
)


class TelegramCommandProvider(Provider):
    scope = Scope.REQUEST
    receive_telegram_updates_interactor = provide(ReceiveTelegramUpdatesInteractor)
    complete_telegram_update_interactor = provide(CompleteTelegramUpdateInteractor)
    accept_audio_interactor = provide(AcceptAudioInteractor)
    telegram_dialog_interactor = provide(TelegramDialogInteractor)
    clear_telegram_dialog_interactor = provide(ClearTelegramDialogInteractor)
    claim_delivery_interactor = provide(ClaimDeliveryInteractor)
    complete_delivery_interactor = provide(CompleteDeliveryInteractor)

    authorize_delivery = provide(AuthorizeDeliveryInteractor)
