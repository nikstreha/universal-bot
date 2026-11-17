from pathlib import Path

from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import event, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)


class SQLAPersistenceConnector:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self._engine: AsyncEngine = create_async_engine(
            "sqlite+aiosqlite:///" + str(path.resolve()), connect_args={"timeout": 10}
        )
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

        @event.listens_for(self._engine.sync_engine, "connect")
        def configure(connection, record):
            connection.isolation_level = None
            cursor = connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.execute("PRAGMA busy_timeout=10000")
            cursor.execute("PRAGMA synchronous=FULL")
            cursor.close()

    async def connect(self) -> None:
        migrations = Path(__file__).parent / "alembic"
        config = Config()
        config.set_main_option("script_location", str(migrations))
        config.set_main_option("version_locations", str(migrations / "version"))
        expected = set(ScriptDirectory.from_config(config).get_heads())
        try:
            async with self._engine.connect() as connection:
                current = set(
                    (
                        await connection.execute(
                            text("SELECT version_num FROM alembic_version")
                        )
                    ).scalars()
                )
        except OperationalError as exc:
            raise RuntimeError(
                "Database schema unavailable; run alembic upgrade head"
            ) from exc
        if current != expected:
            raise RuntimeError("Database schema is outdated; run alembic upgrade head")

    async def disconnect(self) -> None:
        await self._engine.dispose()

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory
