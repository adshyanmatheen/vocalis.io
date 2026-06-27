from __future__ import annotations

import logging

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

logger = logging.getLogger(__name__)

_url = settings.app.database_url
_is_sqlite = _url.startswith("sqlite")

database_engine = create_async_engine(
    _url,
    echo=False,
    pool_size=5 if not _is_sqlite else 1,
    max_overflow=5 if not _is_sqlite else 0,
    pool_recycle=3600,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=database_engine,
    class_=AsyncSession,
    autoflush=False,
    expire_on_commit=False,
)


def is_sqlite() -> bool:
    return _is_sqlite
