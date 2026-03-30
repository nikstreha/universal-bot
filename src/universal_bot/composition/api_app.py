from dataclasses import dataclass

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.aiogram import AiogramProvider
from dishka.integrations.aiogram import setup_dishka as setup_aiogram

from universal_bot.composition.configuration.config import Settings
from universal_bot.composition.ioc.provider_registry import get_provider
from universal_bot.presentation.telegram.router.main_router import root_router


def create_ioc_container(
    configuration: Settings,
    *di_providers: Provider,
) -> AsyncContainer:
    return make_async_container(
        *get_provider(),
        *di_providers,
        AiogramProvider(),
        context={Settings: configuration},
    )


@dataclass(frozen=True)
class BotApplication:
    container: AsyncContainer
    bot_token: str

    async def up(self) -> None:
        bot = Bot(token=self.bot_token)
        dp = Dispatcher(storage=MemoryStorage())

        dp.include_router(root_router)

        setup_aiogram(self.container, dp)

        await dp.start_polling(bot)


async def build_app() -> BotApplication:
    configuration = Settings()  # type: ignore
    container = create_ioc_container(configuration)
    return BotApplication(container=container, bot_token=configuration.BOT_TOKEN)
