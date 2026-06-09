from __future__ import annotations

from typing import (
    Annotated,
)

from litestar import get
from litestar.params import (
    QueryParameter,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.domain.assessment.service import (
    AssessmentService,
)
from app.domain.database.models.user import (
    User,
)
from app.schemas.responses.assessment import (
    AssessmentHistoryItemResponse,
    AssessmentHistoryResponse,
)

assessment_service = AssessmentService()


@get(
    path="/assessment/history",
)
async def get_assessment_history(
    database_session: AsyncSession,
    authenticated_user: User,
    limit: Annotated[
        int,
        QueryParameter(
            ge=1,
            le=100,
        ),
    ] = 10,
    offset: Annotated[
        int,
        QueryParameter(
            ge=0,
        ),
    ] = 0,
) -> AssessmentHistoryResponse:

    (
        attempts,
        total_count,
    ) = await assessment_service.assessment_repository.get_recent_attempts(
        database_session=(database_session),
        user_id=(authenticated_user.id),
        limit=(limit),
        offset=(offset),
    )

    average_score = 0.0

    if attempts:
        average_score = round(
            sum(attempt.overall_score for attempt in attempts) / len(attempts),
            2,
        )

    has_more = (offset + limit) < total_count

    return AssessmentHistoryResponse(
        attempts=[
            (
                AssessmentHistoryItemResponse(
                    id=(attempt.id),
                    target_text=(attempt.target_text),
                    target_difficulty=(attempt.target_difficulty),
                    overall_score=(attempt.overall_score),
                    performance_band=(attempt.performance_band),
                    created_at=str(attempt.created_at),
                )
            )
            for attempt in attempts
        ],
        average_score=(average_score),
        total_attempts=(total_count),
        offset=(offset),
        limit=(limit),
        has_more=(has_more),
    )
