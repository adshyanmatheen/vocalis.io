from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger(__name__)
logger.info("Database engine configured for %s", settings.app.database_url)

database_engine = create_async_engine(
    settings.app.database_url,
    echo=False,
    pool_size=10,
    max_overflow=10,
    pool_recycle=3600,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=database_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)
