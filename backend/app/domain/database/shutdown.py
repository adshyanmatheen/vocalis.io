from __future__ import annotations

import logging

from app.domain.database.session import database_engine

logger = logging.getLogger(__name__)


async def dispose_database_engine() -> None:
    logger.info("Disposing database engine")
    await database_engine.dispose()
