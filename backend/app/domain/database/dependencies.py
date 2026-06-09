from __future__ import annotations

from collections.abc import (
    AsyncGenerator,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.domain.database.session import (
    AsyncSessionLocal,
)


async def provide_database_session() -> AsyncGenerator[AsyncSession]:
    async with AsyncSessionLocal() as database_session:
        yield (database_session)
