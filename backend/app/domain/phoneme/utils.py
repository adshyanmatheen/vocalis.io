from __future__ import annotations

from typing import Any

PHONEME_WEAK_SCORE_THRESHOLD = 0.6


def extract_weak_phonemes(
    phoneme_results: list[dict[str, Any]],
) -> list[str]:
    return sorted(
        {
            result["expected_phoneme"]
            for result in phoneme_results
            if result["phoneme_score"] < PHONEME_WEAK_SCORE_THRESHOLD
        }
    )
