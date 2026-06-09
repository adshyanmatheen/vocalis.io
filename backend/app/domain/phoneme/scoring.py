from __future__ import annotations

import logging
from collections import defaultdict

from app.domain.phoneme.constants import (
    DISTORTION_CONFIDENCE_THRESHOLD,
    EXCELLENT_SCORE_THRESHOLD,
    HIGH_IMPORTANCE_PHONEMES,
    MILD_SEVERITY_THRESHOLD,
    MODERATE_SEVERITY_THRESHOLD,
    NEEDS_MORE_PRACTICE_THRESHOLD,
    ON_TRACK_THRESHOLD,
    PHONEME_ERROR_WEIGHTS,
    PHONEME_SEVERITY_WEIGHT,
    SEVERE_SEVERITY_THRESHOLD,
    STRONG_SCORE_THRESHOLD,
)
from app.domain.phoneme.exceptions import PhonemeScoringError
from app.domain.phoneme.models import (
    ErrorType,
    PerformanceBand,
    PhonemeMatch,
    ScoredPhonemeResult,
    ScoringPayload,
    Severity,
    WordScore,
)

logger = logging.getLogger(__name__)


def get_value(result, key: str):
    if isinstance(result, dict):
        return result[key]

    return getattr(result, key)


def classify_error_type(
    *,
    expected_phoneme: str,
    predicted_phoneme: str,
    confidence_score: float,
    phoneme_duration: float,
) -> ErrorType:

    if confidence_score <= 0.15:
        return ErrorType.DELETION

    if predicted_phoneme != expected_phoneme:
        return ErrorType.SUBSTITUTION

    if confidence_score < DISTORTION_CONFIDENCE_THRESHOLD:
        return ErrorType.DISTORTION

    if phoneme_duration <= 0.04:
        return ErrorType.DISTORTION

    return ErrorType.NONE


def compute_importance_weight(phoneme: str) -> float:

    if phoneme.upper() in HIGH_IMPORTANCE_PHONEMES:
        return 1.35

    return 1.0


def compute_duration_penalty(phoneme_duration: float) -> float:

    if phoneme_duration <= 0.03:
        return 0.35

    if phoneme_duration <= 0.06:
        return 0.15

    return 0.0


def compute_severity_score(
    *, error_type: ErrorType, confidence_score: float, phoneme_duration: float
) -> float:

    confidence_penalty = 1.0 - max(0.0, min(1.0, confidence_score))
    duration_penalty = compute_duration_penalty(phoneme_duration)

    severity_score = (
        confidence_penalty + PHONEME_ERROR_WEIGHTS[error_type] + duration_penalty
    )
    return min(1.0, severity_score)


def severity_from_score(severity_score: float) -> Severity:

    if severity_score < MILD_SEVERITY_THRESHOLD:
        return Severity.NONE

    if severity_score < MODERATE_SEVERITY_THRESHOLD:
        return Severity.MILD

    if severity_score < SEVERE_SEVERITY_THRESHOLD:
        return Severity.MODERATE

    return Severity.SEVERE


def compute_phoneme_score(
    *, confidence_score: float, severity_score: float, importance_weight: float
) -> float:

    base_score = max(
        0.0, confidence_score * (1.0 - (PHONEME_SEVERITY_WEIGHT * severity_score))
    )
    weighted_score = base_score * importance_weight

    return min(1.0, weighted_score)


def performance_band_from_score(score: float) -> PerformanceBand:

    if score >= EXCELLENT_SCORE_THRESHOLD:
        return PerformanceBand.EXCELLENT

    if score >= STRONG_SCORE_THRESHOLD:
        return PerformanceBand.STRONG

    if score >= ON_TRACK_THRESHOLD:
        return PerformanceBand.ON_TRACK

    if score >= NEEDS_MORE_PRACTICE_THRESHOLD:
        return PerformanceBand.NEEDS_MORE_PRACTICE

    return PerformanceBand.NEEDS_CAREFUL_PRACTICE


def score_phoneme_result(result: PhonemeMatch) -> ScoredPhonemeResult:

    phoneme_duration = get_value(result, "end_time") - get_value(result, "start_time")

    error_type = classify_error_type(
        expected_phoneme=(get_value(result, "expected_phoneme")),
        predicted_phoneme=(get_value(result, "predicted_phoneme")),
        confidence_score=(get_value(result, "confidence_score")),
        phoneme_duration=phoneme_duration,
    )

    importance_weight = compute_importance_weight(get_value(result, "expected_phoneme"))

    severity_score = compute_severity_score(
        error_type=error_type,
        confidence_score=(get_value(result, "confidence_score")),
        phoneme_duration=(phoneme_duration),
    )

    severity = severity_from_score(severity_score)

    phoneme_score = compute_phoneme_score(
        confidence_score=(get_value(result, "confidence_score")),
        severity_score=severity_score,
        importance_weight=importance_weight,
    )

    return {
        "expected_phoneme": get_value(result, "expected_phoneme"),
        "predicted_phoneme": get_value(result, "predicted_phoneme"),
        "confidence_score": get_value(result, "confidence_score"),
        "overlap_score": get_value(result, "overlap_score"),
        "start_time": get_value(result, "start_time"),
        "end_time": get_value(result, "end_time"),
        "word": get_value(result, "word"),
        "severity": severity,
        "error_type": error_type,
        "severity_score": round(
            severity_score,
            4,
        ),
        "importance_weight": round(
            importance_weight,
            4,
        ),
        "phoneme_score": round(
            phoneme_score,
            4,
        ),
    }


def compute_word_score(*, word: str, phonemes: list[ScoredPhonemeResult]) -> WordScore:

    weighted_sum = sum(
        phoneme["phoneme_score"] * phoneme["importance_weight"] for phoneme in phonemes
    )
    weight_sum = sum(phoneme["importance_weight"] for phoneme in phonemes) or 1.0
    weighted_score = weighted_sum / weight_sum

    if not phonemes:
        return {
            "word": word,
            "weighted_score": 0.0,
            "average_confidence": 0.0,
            "phoneme_count": 0,
            "performance_band": performance_band_from_score(0.0),
        }

    average_confidence = sum(phoneme["confidence_score"] for phoneme in phonemes) / len(
        phonemes
    )

    return {
        "word": word,
        "weighted_score": round(
            weighted_score,
            4,
        ),
        "average_confidence": round(
            average_confidence,
            4,
        ),
        "phoneme_count": len(phonemes),
        "performance_band": (performance_band_from_score(weighted_score)),
    }


def score_pronunciation(phoneme_results: list[PhonemeMatch]) -> ScoringPayload:

    try:
        scored_phoneme_results = [
            score_phoneme_result(result) for result in phoneme_results
        ]
        phonemes_by_word: dict[str, list[ScoredPhonemeResult]] = defaultdict(list)

        for result in scored_phoneme_results:
            phonemes_by_word[result["word"]].append(result)

        word_scores = [
            compute_word_score(word=word, phonemes=phonemes)
            for word, phonemes in phonemes_by_word.items()
        ]
        overall_score = (
            sum(word["weighted_score"] for word in word_scores) / len(word_scores)
            if word_scores
            else 0.0
        )

        return {
            "phoneme_results": (scored_phoneme_results),
            "word_scores": word_scores,
            "overall_score": round(overall_score, 4),
            "performance_band": (performance_band_from_score(overall_score)),
        }

    except Exception as error:
        logger.exception("Failed to score pronunciation")
        raise PhonemeScoringError("Failed To Score Pronunciation.") from error
