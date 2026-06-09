from __future__ import annotations

from typing import TypedDict

from app.domain.feedback.models import (
    FeedbackPayload,
    PersonalizedFeedbackContext,
)
from app.domain.phoneme.models import (
    ScoredPhonemeResult,
    WordScore,
)


class AssessmentRequest(TypedDict):
    user_id: int
    target_text: str
    audio_path: str


class AssessmentResult(TypedDict):
    overall_score: float
    performance_band: str
    scored_phonemes: list[ScoredPhonemeResult]
    weak_phonemes: list[str]
    word_scores: list[WordScore]
    feedback: FeedbackPayload
    personalization: PersonalizedFeedbackContext


class AssessmentPersistencePayload(TypedDict):
    user_id: int
    target_text: str
    target_difficulty: str
    overall_score: float
    performance_band: str
    phoneme_results: list[ScoredPhonemeResult]
    word_scores: list[WordScore]
    feedback_payload: FeedbackPayload
    weak_phonemes: list[str]


class LearnerAssessmentHistory(TypedDict):
    total_attempts: int
    average_score: float
    strongest_phonemes: list[str]
    weakest_phonemes: list[str]
    recent_trend: str
