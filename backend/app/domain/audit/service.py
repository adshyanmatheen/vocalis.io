from __future__ import annotations

from sqlalchemy import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.database.models.audit_log import AuditLog


async def log_audit_event(
    database_session: AsyncSession,
    *,
    action: str,
    actor_id: int | None = None,
    resource_type: str | None = None,
    resource_id: str | int | None = None,
    details: dict | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> None:
    stmt = insert(AuditLog).values(
        actor_id=actor_id,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id is not None else None,
        details=details,
        ip_address=ip_address,
        user_agent=user_agent,
    )
    await database_session.execute(stmt)
    await database_session.commit()
