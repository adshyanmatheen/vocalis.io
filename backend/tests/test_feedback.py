from __future__ import annotations

from app.domain.feedback.generator import generate_feedback


async def test_generate_feedback_uses_rule_based_fallback_when_groq_is_disabled() -> (
    None
):
    feedback = await generate_feedback(
        target_text="The quick brown fox",
        scoring_payload={
            "overall_score": 0.7,
            "performance_band": "On Track",
            "word_scores": [
                {
                    "word": "quick",
                    "weighted_score": 0.7,
                    "average_confidence": 0.8,
                    "performance_band": "On Track",
                },
            ],
            "phoneme_results": [
                {
                    "expected_phoneme": "k",
                    "predicted_phoneme": "k",
                    "confidence_score": 0.8,
                    "overlap_score": 0.7,
                    "start_time": 0.0,
                    "end_time": 0.2,
                    "word": "quick",
                    "severity": "low",
                    "error_type": "distortion",
                    "severity_score": 0.2,
                    "importance_weight": 1.0,
                    "phoneme_score": 0.7,
                },
            ],
        },
    )

    assert feedback["feedback_provider"] == "fallback"
    assert feedback["feedback_model"] == "rule-based"
    assert len(feedback["action_items"]) == 2
