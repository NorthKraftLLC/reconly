"""Alembic environment configuration."""

import sys
from pathlib import Path

from alembic import context
from logging.config import fileConfig

from app.config import settings
from app.models.base import Base
from app.models import User, Company, InventoryItem, Reconciliation, Discrepancy

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

sys.path.insert(0, str(Path(__file__).parent.parent))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        include_schemas=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine

    url = settings.DATABASE_URL
    connectable = create_async_engine(url)

    async def do_run_migrations() -> None:
        async with connectable.connect() as connection:
            await connection.run_sync(_run_sync_migrations)
        await connectable.dispose()

    def _run_sync_migrations(connection) -> None:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            include_schemas=True,
        )
        with context.begin_transaction():
            context.run_migrations()

    import asyncio
    asyncio.run(do_run_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
