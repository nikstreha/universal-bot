import asyncio
import logging
import os
import signal
from typing import Annotated, Literal

import typer
import uvicorn
from pydantic import ValidationError

from universal_bot.composition.api_app import build_api_app
from universal_bot.composition.logging import configure_logging
from universal_bot.composition.telegram_app import create_telegram_app
from universal_bot.composition.worker_app import create_worker_app
from universal_bot.domain.exception.base import BaseError

cli = typer.Typer(
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_enable=False,
    help="Приватное хранилище и Telegram-транскрибация.",
)


@cli.callback()
def configure() -> None:
    os.umask(0o077)
    configure_logging()


@cli.command()
def api(
    host: Annotated[
        str, typer.Option(help="Адрес или DNS-имя интерфейса API.")
    ] = "127.0.0.1",
    port: Annotated[int, typer.Option(min=1, max=65535)] = 7000,
) -> None:
    """Запустить HTTP API и приём Telegram webhook."""
    uvicorn.run(
        build_api_app(),
        host=host,
        port=port,
        log_level="info",
        proxy_headers=True,
        log_config=None,
        access_log=False,
    )


async def _serve(kind: Literal["bot", "worker"]) -> None:
    loop = asyncio.get_running_loop()
    task = asyncio.current_task()
    loop.add_signal_handler(signal.SIGTERM, task.cancel)
    try:
        application = await (
            create_telegram_app() if kind == "bot" else create_worker_app()
        )
        await application.up()
    finally:
        loop.remove_signal_handler(signal.SIGTERM)


@cli.command()
def bot() -> None:
    """Получать Telegram-обновления и отправлять ответы."""
    asyncio.run(_serve("bot"))


@cli.command()
def worker() -> None:
    """Обрабатывать файлы, корзину и транскрибации."""
    asyncio.run(_serve("worker"))


if __name__ == "__main__":
    try:
        cli()
    except ValidationError as exc:
        fields = ", ".join(".".join(map(str, error["loc"])) for error in exc.errors())
        logging.getLogger(__name__).error(
            "Invalid configuration fields: %s",
            fields,
            extra={"event": "configuration_invalid"},
        )
        raise SystemExit(1) from None
    except BaseError as exc:
        logging.getLogger(__name__).error(
            "Process failed: %s",
            exc.code,
            extra={"event": "process_failed", "error_code": exc.code},
        )
        raise SystemExit(1) from None
    except KeyboardInterrupt, asyncio.CancelledError:
        raise SystemExit(130) from None
    except Exception:
        # Exceptions from HTTP clients can contain a URL with the bot token.
        logging.getLogger(__name__).exception(
            "Process failed", extra={"event": "process_failed"}
        )
        raise SystemExit(1) from None
