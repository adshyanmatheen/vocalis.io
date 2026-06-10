from __future__ import annotations

import asyncio
import logging
from typing import Any

import numpy as np
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.domain.assessment.exceptions import (
    AssessmentPersistenceError,
)
from app.domain.assessment.models import (
    AssessmentPersistencePayload,
    AssessmentRequest,
    AssessmentResult,
)
from app.domain.assessment.repository import (
    AssessmentRepository,
)
from app.domain.feedback.service import (
    FeedbackService,
)
from app.domain.phoneme.models import (
    ScoredPhonemeResult,
    ScoringPayload,
)
from app.domain.phoneme.service import (
    PhonemeService,
)
from app.domain.phoneme.utils import extract_weak_phonemes

logger = logging.getLogger(__name__)


class AssessmentService:
    def __init__(
        self,
        phoneme_service: PhonemeService | None = None,
        feedback_service: FeedbackService | None = None,
        assessment_repository: AssessmentRepository | None = None,
    ) -> None:
        self.phoneme_service = phoneme_service or PhonemeService()
        self.feedback_service = feedback_service or FeedbackService()
        self.assessment_repository = assessment_repository or AssessmentRepository()

    async def analyze_assessment(
        self,
        *,
        database_session: AsyncSession,
        assessment_request: (AssessmentRequest),
        word_segments: list[dict[str, Any]],
        audio_waveform: np.ndarray,
        sample_rate: int,
    ) -> AssessmentResult:
        scoring_payload = await asyncio.to_thread(
            self.phoneme_service.analyze_pronunciation,
            target_text=(assessment_request["target_text"]),
            word_segments=word_segments,
            audio_waveform=audio_waveform,
            sample_rate=sample_rate,
        )

        phoneme_results = scoring_payload["phoneme_results"]

        feedback_response = await self.feedback_service.build_feedback_response(
            target_text=(assessment_request["target_text"]),
            scoring_payload=scoring_payload,
            phoneme_history=phoneme_results,
        )

        weak_phonemes = extract_weak_phonemes(phoneme_results=phoneme_results)

        persistence_payload = self.build_persistence_payload(
            assessment_request=assessment_request,
            scoring_payload=scoring_payload,
            feedback_response=feedback_response,
            weak_phonemes=weak_phonemes,
        )

        await asyncio.gather(
            self.persist_assessment(
                database_session=database_session,
                persistence_payload=persistence_payload,
            ),
            self.update_phoneme_memories(
                database_session=database_session,
                user_id=(assessment_request["user_id"]),
                phoneme_results=phoneme_results,
            ),
        )

        return {
            "overall_score": (scoring_payload["overall_score"]),
            "performance_band": (scoring_payload["performance_band"]),
            "scored_phonemes": (phoneme_results),
            "weak_phonemes": (weak_phonemes),
            "word_scores": (scoring_payload["word_scores"]),
            "feedback": (feedback_response["feedback"]),
            "personalization": (feedback_response["personalization"]),
        }

    def build_persistence_payload(
        self,
        *,
        assessment_request: (AssessmentRequest),
        scoring_payload: (ScoringPayload),
        feedback_response: dict,
        weak_phonemes: list[str],
    ) -> AssessmentPersistencePayload:

        return {
            "user_id": (assessment_request["user_id"]),
            "target_text": (assessment_request["target_text"]),
            "target_difficulty": ("medium"),
            "overall_score": (scoring_payload["overall_score"]),
            "performance_band": (scoring_payload["performance_band"]),
            "phoneme_results": (scoring_payload["phoneme_results"]),
            "word_scores": (scoring_payload["word_scores"]),
            "feedback_payload": (feedback_response["feedback"]),
            "weak_phonemes": (weak_phonemes),
        }

    async def persist_assessment(
        self,
        *,
        database_session: AsyncSession,
        persistence_payload: (AssessmentPersistencePayload),
    ) -> None:
        try:
            await self.assessment_repository.create_attempt(
                database_session=database_session,
                payload=persistence_payload,
            )

        except Exception as error:
            logger.exception("Assessment persistence failed")
            raise (
                AssessmentPersistenceError("Failed To Persist Assessment.")
            ) from error

    async def update_phoneme_memories(
        self,
        *,
        database_session: AsyncSession,
        user_id: int,
        phoneme_results: list[ScoredPhonemeResult],
    ) -> None:
        phoneme_names = list({r["expected_phoneme"] for r in phoneme_results})

        existing_memories = (
            await self.assessment_repository.get_phoneme_memories_by_user_and_phonemes(
                database_session=database_session,
                user_id=user_id,
                phonemes=phoneme_names,
            )
        )

        tasks = []
        for result in phoneme_results:
            phoneme = result["expected_phoneme"]
            memory = existing_memories.get(phoneme)

            if memory is None:
                tasks.append(
                    self.assessment_repository.create_phoneme_memory(
                        database_session=database_session,
                        user_id=user_id,
                        phoneme=phoneme,
                        phoneme_score=(result["phoneme_score"]),
                        severity_score=(result["severity_score"]),
                        error_type=(result["error_type"]),
                    )
                )
            else:
                tasks.append(
                    self.assessment_repository.update_phoneme_memory(
                        database_session=database_session,
                        memory=memory,
                        phoneme_score=(result["phoneme_score"]),
                        severity_score=(result["severity_score"]),
                        error_type=(result["error_type"]),
                    )
                )

        if tasks:
            await asyncio.gather(*tasks)
