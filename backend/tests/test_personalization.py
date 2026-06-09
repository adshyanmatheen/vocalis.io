from __future__ import annotations

from app.domain.feedback.personalization import (
    analyze_personalization,
    analyze_phoneme_trend,
    build_consistency_summary,
    build_focus_phoneme_memory,
    build_personalized_context,
    build_trend_summary,
    compute_consistency_score,
    compute_weighted_average,
    derive_consistency_direction,
    derive_focus_phonemes,
    derive_trend_confidence_label,
    derive_trend_direction,
)
from app.domain.phoneme.models import ScoredPhonemeResult


def _make_phoneme_result(
    phoneme: str = "AA",
    score: float = 0.8,
    severity: float = 0.2,
    error_type: str = "substitution",
    end_time: float = 10.0,
) -> ScoredPhonemeResult:
    return {
        "expected_phoneme": phoneme,
        "phoneme_score": score,
        "severity_score": severity,
        "error_type": error_type,
        "start_time": end_time - 1.0,
        "end_time": end_time,
        "expected_start_time": 0.0,
        "expected_end_time": 1.0,
        "predicted_phoneme": phoneme,
    }


class TestComputeWeightedAverage:
    def test_empty_list(self) -> None:
        assert compute_weighted_average([]) == 0.0

    def test_single_value(self) -> None:
        assert compute_weighted_average([0.8]) == 0.8

    def test_multiple_values_decay(self) -> None:
        result = compute_weighted_average([0.5, 1.0])
        assert 0.5 < result < 1.0

    def test_all_same_values(self) -> None:
        assert compute_weighted_average([0.7, 0.7, 0.7]) == 0.7


class TestDeriveTrendDirection:
    def test_improving(self) -> None:
        assert derive_trend_direction(0.1) == "improving"

    def test_declining(self) -> None:
        assert derive_trend_direction(-0.1) == "declining"

    def test_stable(self) -> None:
        assert derive_trend_direction(0.0) == "stable"

    def test_barely_improving(self) -> None:
        assert derive_trend_direction(0.05) == "stable"

    def test_barely_declining(self) -> None:
        assert derive_trend_direction(-0.05) == "stable"


class TestDeriveConsistencyDirection:
    def test_improving_high_consistency(self) -> None:
        assert derive_consistency_direction(0.9) == "improving"

    def test_declining_low_consistency(self) -> None:
        assert derive_consistency_direction(0.1) == "declining"

    def test_stable_mid_consistency(self) -> None:
        assert derive_consistency_direction(0.7) == "stable"


class TestDeriveTrendConfidenceLabel:
    def test_high(self) -> None:
        assert derive_trend_confidence_label(0.9) == "high"

    def test_medium(self) -> None:
        assert derive_trend_confidence_label(0.7) == "medium"

    def test_low(self) -> None:
        assert derive_trend_confidence_label(0.1) == "low"


class TestComputeConsistencyScore:
    def test_single_score(self) -> None:
        assert compute_consistency_score([0.8]) == 1.0

    def test_identical_scores(self) -> None:
        assert compute_consistency_score([0.8, 0.8, 0.8]) == 1.0

    def test_varied_scores(self) -> None:
        score = compute_consistency_score([0.5, 0.9])
        assert 0.0 < score < 1.0

    def test_extreme_range(self) -> None:
        assert compute_consistency_score([0.0, 1.0]) == 0.0


class TestBuildTrendSummary:
    def test_improving(self) -> None:
        summary = build_trend_summary(phoneme="AA", trend_direction="improving")
        assert "Improving" in summary
        assert "/AA/" in summary

    def test_declining(self) -> None:
        summary = build_trend_summary(phoneme="AA", trend_direction="declining")
        assert "Declining" in summary or "Needs" in summary

    def test_stable(self) -> None:
        summary = build_trend_summary(phoneme="AA", trend_direction="stable")
        assert "Stable" in summary


class TestBuildConsistencySummary:
    def test_improving(self) -> None:
        summary = build_consistency_summary(
            phoneme="AA", consistency_direction="improving"
        )
        assert "Consistent" in summary

    def test_declining(self) -> None:
        summary = build_consistency_summary(
            phoneme="AA", consistency_direction="declining"
        )
        assert "Inconsistent" in summary

    def test_stable(self) -> None:
        summary = build_consistency_summary(
            phoneme="AA", consistency_direction="stable"
        )
        assert "Moderate" in summary


class TestAnalyzePhonemeTrend:
    def test_single_score(self) -> None:
        trend = analyze_phoneme_trend(phoneme="AA", scores=[0.8])
        assert trend["phoneme"] == "AA"
        assert trend["recent_scores"] == [0.8]

    def test_multiple_scores(self) -> None:
        trend = analyze_phoneme_trend(phoneme="AA", scores=[0.5, 0.7, 0.9])
        assert len(trend["recent_scores"]) == 3
        assert "trend_direction" in trend
        assert "trend_summary" in trend
        assert "consistency_score" in trend


class TestBuildFocusPhonemeMemory:
    def test_single_result(self) -> None:
        results = [_make_phoneme_result(phoneme="AA")]
        memory = build_focus_phoneme_memory(phoneme="AA", phoneme_results=results)
        assert memory["phoneme"] == "AA"
        assert memory["total_occurrences"] == 1
        assert memory["weak_occurrences"] == 0
        assert "trend" in memory

    def test_weak_phoneme_detected(self) -> None:
        results = [_make_phoneme_result(phoneme="AA", score=0.3)]
        memory = build_focus_phoneme_memory(phoneme="AA", phoneme_results=results)
        assert memory["weak_occurrences"] == 1


class TestDeriveFocusPhonemes:
    def test_sorts_by_average_score_ascending(self) -> None:
        phonemes = [
            {"phoneme": "AA", "average_score": 0.9, "weak_occurrences": 0},
            {"phoneme": "BB", "average_score": 0.5, "weak_occurrences": 2},
        ]
        result = derive_focus_phonemes(phonemes)
        assert result[0]["phoneme"] == "BB"


class TestBuildPersonalizedContext:
    def test_empty_phonemes(self) -> None:
        context = build_personalized_context(focus_phonemes=[])
        assert context["current_focus"] is None

    def test_with_phonemes(self) -> None:
        focus = [
            {
                "phoneme": "AA",
                "total_occurrences": 3,
                "weak_occurrences": 1,
                "average_score": 0.6,
                "average_severity_score": 0.3,
                "recent_weighted_score": 0.65,
                "common_error_types": ["substitution"],
                "last_seen_at": 10.0,
                "trend": {
                    "phoneme": "AA",
                    "recent_scores": [0.6],
                    "weighted_trend_delta": 0.0,
                    "trend_direction": "stable",
                    "trend_summary": "Your /AA/ Pronunciation Remains Relatively Stable.",
                    "consistency_score": 1.0,
                    "consistency_direction": "stable",
                    "consistency_summary": "Your /AA/ Pronunciation Shows Moderate Consistency.",
                    "trend_confidence": 0.1,
                    "trend_confidence_label": "low",
                },
            }
        ]
        context = build_personalized_context(focus_phonemes=focus)
        assert context["current_focus"] == "AA"


class TestAnalyzePersonalization:
    def test_empty_history(self) -> None:
        result = analyze_personalization(phoneme_history=[])
        assert result["attempt_count"] == 0
        assert result["average_score"] == 0.0

    def test_single_result(self) -> None:
        history = [_make_phoneme_result(phoneme="AA", score=0.85)]
        result = analyze_personalization(phoneme_history=history)
        assert result["attempt_count"] == 1
        assert result["average_score"] == 0.85
        assert result["last_attempt_at"] == 10.0

    def test_multiple_phonemes(self) -> None:
        history = [
            _make_phoneme_result(phoneme="AA", score=0.8),
            _make_phoneme_result(phoneme="AA", score=0.9),
            _make_phoneme_result(phoneme="BB", score=0.5),
        ]
        result = analyze_personalization(phoneme_history=history)
        assert result["attempt_count"] == 3
        assert len(result["focus_phonemes"]) == 2

    def test_average_score(self) -> None:
        history = [
            _make_phoneme_result(phoneme="AA", score=0.6),
            _make_phoneme_result(phoneme="AA", score=0.8),
        ]
        result = analyze_personalization(phoneme_history=history)
        assert result["average_score"] == 0.7
