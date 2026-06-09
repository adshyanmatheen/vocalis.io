from __future__ import annotations

import logging
from collections import defaultdict
from statistics import mean

from app.domain.feedback.constants import (
    DECLINE_DELTA_THRESHOLD,
    HIGH_CONSISTENCY_THRESHOLD,
    HIGH_TREND_CONFIDENCE_THRESHOLD,
    IMPROVEMENT_DELTA_THRESHOLD,
    LOW_CONSISTENCY_THRESHOLD,
    MEDIUM_TREND_CONFIDENCE_THRESHOLD,
    PHONEME_MEMORY_DECAY_FACTOR,
    RECENT_PHONEME_TREND_LIMIT,
    WEAK_PHONEME_SCORE_THRESHOLD,
)
from app.domain.feedback.exceptions import PersonalizationAnalysisError
from app.domain.feedback.models import (
    ConsistencyDirection,
    FocusPhonemeMemory,
    FocusPhonemeTrend,
    LearnerPersonalizationSummary,
    PersonalizedFeedbackContext,
    TrendConfidenceLabel,
    TrendDirection,
)
from app.domain.phoneme.models import ScoredPhonemeResult

logger = logging.getLogger(__name__)


def compute_weighted_average(values: list[float]) -> float:
    if not values:
        return 0.0

    weighted_sum = 0.0
    total_weight = 0.0

    for index, value in enumerate(reversed(values)):
        weight = PHONEME_MEMORY_DECAY_FACTOR**index

        weighted_sum += value * weight
        total_weight += weight

    return weighted_sum / total_weight


def derive_trend_direction(
    trend_delta: float,
) -> TrendDirection:
    if trend_delta >= IMPROVEMENT_DELTA_THRESHOLD:
        return "improving"

    if trend_delta <= DECLINE_DELTA_THRESHOLD:
        return "declining"

    return "stable"


def derive_consistency_direction(consistency_score: float) -> ConsistencyDirection:
    if consistency_score >= HIGH_CONSISTENCY_THRESHOLD:
        return "improving"

    if consistency_score <= LOW_CONSISTENCY_THRESHOLD:
        return "declining"

    return "stable"


def derive_trend_confidence_label(confidence_score: float) -> TrendConfidenceLabel:

    if confidence_score >= HIGH_TREND_CONFIDENCE_THRESHOLD:
        return "high"

    if confidence_score >= MEDIUM_TREND_CONFIDENCE_THRESHOLD:
        return "medium"

    return "low"


def compute_consistency_score(scores: list[float]) -> float:
    if len(scores) <= 1:
        return 1.0

    score_range = max(scores) - min(scores)

    return max(0.0, 1.0 - score_range)


def build_trend_summary(*, phoneme: str, trend_direction: TrendDirection) -> str:

    if trend_direction == "improving":
        return f"Your /{phoneme}/ Pronunciation Is Improving Steadily."

    if trend_direction == "declining":
        return f"Your /{phoneme}/ Pronunciation Still Needs More Consistent Practice."

    return f"Your /{phoneme}/ Pronunciation Remains Relatively Stable."


def build_consistency_summary(
    *, phoneme: str, consistency_direction: ConsistencyDirection
) -> str:

    if consistency_direction == "improving":
        return f"Your /{phoneme}/ Pronunciation Is Becoming More Consistent."

    if consistency_direction == "declining":
        return f"Your /{phoneme}/ Pronunciation Is Still Inconsistent."

    return f"Your /{phoneme}/ Pronunciation Shows Moderate Consistency."


def analyze_phoneme_trend(*, phoneme: str, scores: list[float]) -> FocusPhonemeTrend:

    recent_scores = scores[-RECENT_PHONEME_TREND_LIMIT:]

    weighted_average = compute_weighted_average(recent_scores)
    historical_average = mean(recent_scores)

    trend_delta = weighted_average - historical_average
    consistency_score = compute_consistency_score(recent_scores)

    trend_direction = derive_trend_direction(trend_delta)
    consistency_direction = derive_consistency_direction(consistency_score)
    trend_confidence = min(1.0, len(recent_scores) / 10)

    return {
        "phoneme": phoneme,
        "recent_scores": recent_scores,
        "weighted_trend_delta": round(trend_delta, 4),
        "trend_direction": trend_direction,
        "trend_summary": (
            build_trend_summary(phoneme=phoneme, trend_direction=trend_direction)
        ),
        "consistency_score": round(consistency_score, 4),
        "consistency_direction": (consistency_direction),
        "consistency_summary": (
            build_consistency_summary(
                phoneme=phoneme, consistency_direction=consistency_direction
            )
        ),
        "trend_confidence": round(
            trend_confidence,
            4,
        ),
        "trend_confidence_label": (derive_trend_confidence_label(trend_confidence)),
    }


def build_focus_phoneme_memory(
    *, phoneme: str, phoneme_results: list[ScoredPhonemeResult]
) -> FocusPhonemeMemory:
    scores = [result["phoneme_score"] for result in phoneme_results]
    severity_scores = [result["severity_score"] for result in phoneme_results]

    weak_occurrences = sum(
        1 for score in scores if score < WEAK_PHONEME_SCORE_THRESHOLD
    )
    trend = analyze_phoneme_trend(phoneme=phoneme, scores=scores)

    common_error_types = sorted({result["error_type"] for result in phoneme_results})

    return {
        "phoneme": phoneme,
        "total_occurrences": len(phoneme_results),
        "weak_occurrences": weak_occurrences,
        "average_score": round(mean(scores), 4),
        "average_severity_score": round(mean(severity_scores), 4),
        "recent_weighted_score": round(compute_weighted_average(scores), 4),
        "common_error_types": (common_error_types),
        "last_seen_at": phoneme_results[-1]["end_time"],  # pyrefly: ignore
        "trend": trend,
    }


def derive_focus_phonemes(
    focus_memories: list[FocusPhonemeMemory],
) -> list[FocusPhonemeMemory]:
    return sorted(
        focus_memories,
        key=lambda memory: (memory["average_score"], -memory["weak_occurrences"]),
    )


def build_personalized_context(
    *, focus_phonemes: list[FocusPhonemeMemory]
) -> PersonalizedFeedbackContext:

    if not focus_phonemes:
        return {
            "current_focus": None,
            "recurring_sound_note": None,
            "improvement_note": None,
            "consistency_note": None,
            "focus_phonemes": [],
        }

    primary_focus = focus_phonemes[0]
    trend = primary_focus["trend"]

    return {
        "current_focus": (primary_focus["phoneme"]),
        "recurring_sound_note": (
            f"You repeatedly struggle with the /{primary_focus['phoneme']}/ sound."
        ),
        "improvement_note": (trend["trend_summary"]),
        "consistency_note": (trend["consistency_summary"]),
        "focus_phonemes": focus_phonemes,
    }


def analyze_personalization(
    *, phoneme_history: list[ScoredPhonemeResult]
) -> LearnerPersonalizationSummary:
    try:
        phoneme_groups: dict[str, list[ScoredPhonemeResult]] = defaultdict(list)

        for result in phoneme_history:
            phoneme_groups[result["expected_phoneme"]].append(result)

        focus_memories = [
            build_focus_phoneme_memory(phoneme=phoneme, phoneme_results=results)
            for phoneme, results in phoneme_groups.items()
        ]
        focus_memories = derive_focus_phonemes(focus_memories)

        personalized_context = build_personalized_context(focus_phonemes=focus_memories)

        average_score = (
            mean(result["phoneme_score"] for result in phoneme_history)
            if phoneme_history
            else 0.0
        )

        return {
            "attempt_count": len(phoneme_history),
            "average_score": round(average_score, 4),
            "last_attempt_at": (
                phoneme_history[-1]["end_time"] if phoneme_history else None  # pyrefly: ignore
            ),
            "recent_attempts": [],
            "focus_phonemes": (focus_memories),
            "current_focus": (personalized_context["current_focus"]),
            "recurring_sound_note": (personalized_context["recurring_sound_note"]),
            "improvement_note": (personalized_context["improvement_note"]),
            "consistency_note": (personalized_context["consistency_note"]),
        }

    except Exception as error:
        logger.exception("Failed to analyze learner personalization")
        raise PersonalizationAnalysisError(
            "Failed To Analyze Learner Personalization."
        ) from error
