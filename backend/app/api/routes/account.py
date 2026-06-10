from __future__ import annotations

from litestar import get
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.account.repository import AccountRepository
from app.domain.database.models.user import User
from app.schemas.responses.account import AccountSummaryResponse

account_repository = AccountRepository()


@get(
    path="/account/summary",
    operation_id="getAccountSummary",
    summary="Get Account Summary",
    description="This Route Returns A Comprehensive Summary Of The Authenticated User Account Statistics, Including Their Total Assessment Count, Average Performance Metrics, And Other Account-Level Data.",
    tags=["Account"],
)
async def get_account_summary(
    database_session: AsyncSession,
    authenticated_user: User,
) -> AccountSummaryResponse:
    return await account_repository.build_summary(
        database_session=database_session,
        user=authenticated_user,
    )
