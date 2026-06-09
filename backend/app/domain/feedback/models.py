from __future__ import annotations

from typing import Literal, TypedDict

TrendDirection = Literal["improving", "stable", "declining"]
ConsistencyDirection = Literal[
    "improving",
    "stable",
    "declining",
]
TrendConfidenceLabel = Literal["high", "medium", "low"]


class WeakPhonemeFeedback(TypedDict):
    phoneme: str
    word: str
    severity: str
    error_type: str
    phoneme_score: float
    articulation_hint: str


class WeakWordFeedback(TypedDict):
    word: str
    weighted_score: float
    average_confidence: float
    performance_band: str


class FeedbackPayload(TypedDict):
    summary: str
    action_items: list[str]
    encouragement: str
    feedback_provider: str
    feedback_model: str


class FocusPhonemeTrend(TypedDict):
    phoneme: str
    recent_scores: list[float]
    weighted_trend_delta: float
    trend_direction: TrendDirection
    trend_summary: str
    consistency_score: float
    consistency_direction: ConsistencyDirection
    consistency_summary: str
    trend_confidence: float
    trend_confidence_label: TrendConfidenceLabel


class FocusPhonemeMemory(TypedDict):
    phoneme: str
    total_occurrences: int
    weak_occurrences: int
    average_score: float
    average_severity_score: float
    recent_weighted_score: float
    common_error_types: list[str]
    last_seen_at: str
    trend: FocusPhonemeTrend


class PersonalizedFeedbackContext(TypedDict):
    current_focus: str | None
    recurring_sound_note: str | None
    improvement_note: str | None
    consistency_note: str | None
    focus_phonemes: list[FocusPhonemeMemory]


class LearnerAttemptSummary(TypedDict):
    id: int
    target_text: str
    target_difficulty: str
    overall_score: float
    performance_band: str
    created_at: str


class LearnerPersonalizationSummary(TypedDict):
    attempt_count: int
    average_score: float
    last_attempt_at: str | None
    recent_attempts: list[LearnerAttemptSummary]
    focus_phonemes: list[FocusPhonemeMemory]
    current_focus: str | None
    recurring_sound_note: str | None
    improvement_note: str | None
    consistency_note: str | None


class GeneratedCoachingFeedback(TypedDict):
    summary: str
    prioritized_phonemes: list[str]
    articulation_guidance: list[str]
    recommended_focus: list[str]
    encouragement: str


class AdaptiveRecommendation(TypedDict):
    focus_phonemes: list[str]
    recommended_difficulty: str
    recommended_category: str | None
    rationale: str
