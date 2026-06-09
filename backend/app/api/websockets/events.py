from __future__ import annotations

from typing import Any

from msgspec import Struct


class AssessmentStartedEvent(Struct, kw_only=True):
    type: str = "assessment_started"
    target_text: str
    sample_rate: int


class PartialFeedbackEvent(Struct, kw_only=True):
    type: str = "partial_feedback"
    overall_score: float
    weak_phonemes: list[str]
    word_scores: list[dict[str, Any]]
    performance_band: str


class AssessmentCompletedEvent(Struct, kw_only=True):
    type: str = "assessment_completed"
    overall_score: float
    performance_band: str
    feedback: dict[str, Any]
    weak_phonemes: list[str]
    word_scores: list[dict[str, Any]]


class AssessmentErrorEvent(Struct, kw_only=True):
    type: str = "assessment_error"
    message: str
