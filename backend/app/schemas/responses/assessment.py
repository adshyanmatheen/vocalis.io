from __future__ import annotations

from msgspec import (
    Struct,
)

from app.domain.feedback.models import (
    FeedbackPayload,
    PersonalizedFeedbackContext,
)
from app.domain.phoneme.models import (
    ScoredPhonemeResult,
)


class AssessmentWordScoreResponse(Struct, kw_only=True):
    word: str
    weighted_score: float
    average_confidence: float
    performance_band: str


class AssessmentAnalyzeResponse(Struct, kw_only=True):
    overall_score: float
    performance_band: str
    weak_phonemes: list[str]
    scored_phonemes: list[ScoredPhonemeResult]
    word_scores: list[AssessmentWordScoreResponse]
    feedback: FeedbackPayload
    personalization: PersonalizedFeedbackContext


class AssessmentHistoryItemResponse(Struct, kw_only=True):
    id: int
    target_text: str
    target_difficulty: str
    overall_score: float
    performance_band: str
    created_at: str


class AssessmentHistoryResponse(Struct, kw_only=True):
    attempts: list[AssessmentHistoryItemResponse]
    average_score: float
    total_attempts: int
    offset: int
    limit: int
    has_more: bool
