from __future__ import annotations

import logging

from alembic import command
from alembic.config import Config

from app.core.config import settings
from app.domain.database.base import Base
from app.domain.database.models import import_database_models
from app.domain.database.session import database_engine

logger = logging.getLogger(__name__)


async def initialize_database():
    if settings.app.environment != "testing":
        await run_migrations()
        return

    import_database_models()

    async with database_engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def run_migrations() -> None:
    def migrate() -> None:
        alembic_cfg = Config("alembic.ini")
        command.upgrade(alembic_cfg, "head")

    import asyncio

    await asyncio.to_thread(migrate)
