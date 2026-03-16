import asyncio
import logging

import typer

from universal_bot.composition.api_app import build_app

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

cli = typer.Typer(no_args_is_help=True)


@cli.command()
def api() -> None:
    async def _run():
        app = await build_app()
        await app.up()

    try:
        asyncio.run(_run())
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logger.exception(f"Worker crashed: {e}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    cli()
