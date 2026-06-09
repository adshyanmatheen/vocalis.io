from __future__ import annotations

import logging
import subprocess
from pathlib import Path

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
    backend_root = Path(__file__).resolve().parents[3]
    alembic_path = backend_root / ".venv" / "bin" / "alembic"

    if not alembic_path.exists():
        logger.warning(
            "Alembic executable not found at %s; skipping migrations.", alembic_path
        )
        return

    def migrate() -> None:
        result = subprocess.run(
            [str(alembic_path), "upgrade", "head"],
            cwd=backend_root,
            check=True,
            capture_output=True,
            text=True,
        )
        if result.stdout:
            logger.info("Migration output: %s", result.stdout.strip())
        if result.stderr:
            logger.warning("Migration stderr: %s", result.stderr.strip())

    import asyncio

    await asyncio.to_thread(migrate)
