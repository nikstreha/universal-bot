import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy import Connection, event, pool
from sqlalchemy.ext.asyncio import create_async_engine

from universal_bot.composition.configuration.app_configuration import AppConfiguration
from universal_bot.infrastructure.persistence.sqla.mapper.all import map_tables
from universal_bot.infrastructure.persistence.sqla.registry import mapping_registry

configuration = AppConfiguration.model_validate({}).persistence
configuration.database_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
config = context.config
config.set_main_option("sqlalchemy.url", configuration.dsn.replace("%", "%%"))
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
map_tables()
target_metadata = mapping_registry.metadata


def include_name(name, type_, parent_names):
    return type_ != "table" or name in target_metadata.tables


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,
        compare_type=True,
        transactional_ddl=True,
        include_name=include_name,
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    engine = create_async_engine(configuration.dsn, poolclass=pool.NullPool)

    @event.listens_for(engine.sync_engine, "connect")
    def configure_sqlite(connection, record):
        connection.isolation_level = None
        cursor = connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA busy_timeout=10000")
        cursor.execute("PRAGMA synchronous=FULL")
        cursor.close()

    @event.listens_for(engine.sync_engine, "begin")
    def begin_sqlite(connection):
        connection.exec_driver_sql("BEGIN IMMEDIATE")

    try:
        async with engine.connect() as connection:
            await connection.run_sync(do_run_migrations)
    finally:
        await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_async_migrations())
