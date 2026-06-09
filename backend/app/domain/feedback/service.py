from __future__ import annotations

from app.domain.feedback.generator import generate_feedback
from app.domain.feedback.models import (
    FeedbackPayload,
    LearnerPersonalizationSummary,
)
from app.domain.feedback.personalization import analyze_personalization
from app.domain.phoneme.models import (
    ScoredPhonemeResult,
    ScoringPayload,
)


class FeedbackService:
    async def generate_pronunciation_feedback(
        self,
        *,
        target_text: str,
        scoring_payload: ScoringPayload,
    ) -> FeedbackPayload:
        return await generate_feedback(
            target_text=target_text, scoring_payload=scoring_payload
        )

    def analyze_learner_progress(
        self, *, phoneme_history: list[ScoredPhonemeResult]
    ) -> LearnerPersonalizationSummary:
        return analyze_personalization(phoneme_history=phoneme_history)

    async def build_feedback_response(
        self,
        *,
        target_text: str,
        scoring_payload: ScoringPayload,
        phoneme_history: list[ScoredPhonemeResult] | None = None,
    ) -> dict:
        phoneme_history = phoneme_history or []
        personalization_summary = self.analyze_learner_progress(
            phoneme_history=phoneme_history
        )

        feedback_payload = await self.generate_pronunciation_feedback(
            target_text=target_text, scoring_payload=scoring_payload
        )

        return {
            "feedback": feedback_payload,
            "personalization": personalization_summary,
            "overall_score": scoring_payload["overall_score"],
            "performance_band": scoring_payload["performance_band"],
            "focus_phonemes": [
                memory["phoneme"]
                for memory in personalization_summary["focus_phonemes"]
            ],
        }
