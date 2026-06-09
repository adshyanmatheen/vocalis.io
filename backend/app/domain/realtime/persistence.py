from __future__ import annotations

import msgspec
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.websockets.models import (
    IncomingMessageMetadata,
)
from app.domain.assessment.repository import (
    AssessmentRepository,
)
from app.domain.phoneme.models import (
    ScoringPayload,
)
from app.domain.realtime.service import (
    realtime_assessment_service,
)

assessment_repository = AssessmentRepository()


async def store_realtime_assessment(
    *,
    database_session: AsyncSession,
    user_id: int,
    target_text: str,
    scoring_payload: ScoringPayload,
    duration_seconds: float,
    message_metadata: list[IncomingMessageMetadata],
) -> None:
    feedback_payload = realtime_assessment_service.build_completion_feedback(
        scoring_payload=scoring_payload,
        duration_seconds=duration_seconds,
    )
    feedback_payload["realtime"]["messages"] = [
        msgspec.to_builtins(message) for message in message_metadata
    ]

    await assessment_repository.create_attempt(
        database_session=database_session,
        payload={
            "user_id": user_id,
            "target_text": target_text,
            "target_difficulty": "realtime",
            "overall_score": scoring_payload["overall_score"],
            "performance_band": scoring_payload["performance_band"],
            "phoneme_results": msgspec.to_builtins(scoring_payload["phoneme_results"]),
            "word_scores": msgspec.to_builtins(scoring_payload["word_scores"]),
            "feedback_payload": feedback_payload,  # pyrefly: ignore
            "weak_phonemes": realtime_assessment_service.extract_weak_phonemes(
                scoring_payload=scoring_payload,
            ),
        },
    )
