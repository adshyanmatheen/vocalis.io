from __future__ import annotations

import logging

from app.core.rate_limiter import assessment_limiter

logger = logging.getLogger(__name__)


class AssessmentRateLimiter:
    async def is_rate_limited(self, *, user_id: int) -> bool:
        return await assessment_limiter.is_limited(str(user_id))

    async def record_attempt(self, *, user_id: int) -> None:
        await assessment_limiter.record(str(user_id))


assessment_rate_limiter = AssessmentRateLimiter()
