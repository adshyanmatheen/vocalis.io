from __future__ import annotations

import logging
from collections import defaultdict
from datetime import UTC, datetime, timedelta

logger = logging.getLogger(__name__)

ASSESSMENT_RATE_LIMIT_WINDOW_SECONDS = 60
ASSESSMENT_RATE_LIMIT_ATTEMPTS = 10


class AssessmentRateLimiter:
    def __init__(self) -> None:
        self.user_attempts: dict[int, list[datetime]] = defaultdict(list)

    def is_rate_limited(self, *, user_id: int) -> bool:
        now = datetime.now(UTC)
        cutoff = now - timedelta(seconds=ASSESSMENT_RATE_LIMIT_WINDOW_SECONDS)

        self.user_attempts[user_id] = [
            attempt for attempt in self.user_attempts[user_id] if attempt > cutoff
        ]

        return len(self.user_attempts[user_id]) >= ASSESSMENT_RATE_LIMIT_ATTEMPTS

    def record_attempt(self, *, user_id: int) -> None:
        self.user_attempts[user_id].append(datetime.now(UTC))


assessment_rate_limiter = AssessmentRateLimiter()
