from __future__ import annotations

import logging
import random

from app.domain.target.constants import (
    DEFAULT_PHONEME_MATCH_SCORE,
    DEFAULT_TARGET_SELECTION_LIMIT,
    DIFFICULTY_WEIGHT,
    MAXIMUM_TARGET_HISTORY_SIZE,
    MINIMUM_PHONEME_MATCH_SCORE,
    PHONEME_BALANCING_WEIGHT,
    RECENCY_PENALTY_WEIGHT,
    TARGET_SELECTION_RANDOMIZATION_FACTOR,
)
from app.domain.target.exceptions import TargetSelectionError
from app.domain.target.models import TargetSelectionResult, TargetText

logger = logging.getLogger(__name__)


def compute_phoneme_match_score(target: TargetText, focus_phonemes: set[str]) -> float:

    if not focus_phonemes:
        return DEFAULT_PHONEME_MATCH_SCORE

    matched_phonemes = target.phoneme_inventory & focus_phonemes
    return len(matched_phonemes) / len(focus_phonemes)


def compute_difficulty_score(target: TargetText, preferred_difficulty: str) -> float:

    if target.difficulty == preferred_difficulty:
        return 1.0

    return 0.5


def compute_recency_penalty(target: TargetText, recent_target_ids: list[str]) -> float:

    if target.id not in recent_target_ids:
        return 0.0

    reverse_index = recent_target_ids[::-1].index(target.id)
    return (reverse_index + 1) / MAXIMUM_TARGET_HISTORY_SIZE


def compute_selection_score(
    *, phoneme_match_score: float, difficulty_score: float, recency_penalty_score: float
) -> float:

    weighted_score = (
        (phoneme_match_score * PHONEME_BALANCING_WEIGHT)
        + (difficulty_score * DIFFICULTY_WEIGHT)
        - (recency_penalty_score * RECENCY_PENALTY_WEIGHT)
    )
    randomized_bonus = random.uniform(0.0, TARGET_SELECTION_RANDOMIZATION_FACTOR)

    return weighted_score + randomized_bonus


def filter_targets(
    *,
    targets: tuple[TargetText, ...],
    difficulty: str | None,
    category: str | None,
) -> list[TargetText]:

    filtered_targets = list(targets)

    if difficulty:
        filtered_targets = [
            target for target in filtered_targets if target.difficulty == difficulty
        ]

    if category:
        filtered_targets = [
            target for target in filtered_targets if target.category == category
        ]

    return filtered_targets


def select_best_targets(
    *,
    targets: tuple[TargetText, ...],
    focus_phonemes: set[str] | None = None,
    recent_target_ids: list[str] | None = None,
    difficulty: str | None = None,
    category: str | None = None,
    limit: int = DEFAULT_TARGET_SELECTION_LIMIT,
) -> list[TargetSelectionResult]:

    try:
        filtered_targets = filter_targets(
            targets=targets, difficulty=difficulty, category=category
        )

        if not filtered_targets:
            return []

        focus_phonemes = focus_phonemes or set()
        recent_target_ids = recent_target_ids or []

        selection_results: list[TargetSelectionResult] = []

        for target in filtered_targets:
            phoneme_match_score = compute_phoneme_match_score(target, focus_phonemes)

            if focus_phonemes and phoneme_match_score < MINIMUM_PHONEME_MATCH_SCORE:
                continue

            difficulty_score = compute_difficulty_score(
                target, difficulty or target.difficulty
            )

            recency_penalty_score = compute_recency_penalty(target, recent_target_ids)

            final_selection_score = compute_selection_score(
                phoneme_match_score=phoneme_match_score,
                difficulty_score=difficulty_score,
                recency_penalty_score=recency_penalty_score,
            )
            matched_focus_phonemes = tuple(
                sorted(target.phoneme_inventory & focus_phonemes)
            )

            selection_results.append(
                TargetSelectionResult(
                    target=target,
                    matched_focus_phonemes=matched_focus_phonemes,
                    phoneme_match_score=round(phoneme_match_score, 4),
                    difficulty_score=round(difficulty_score, 4),
                    recency_penalty_score=round(recency_penalty_score, 4),
                    final_selection_score=round(final_selection_score, 4),
                )
            )

        selection_results.sort(
            key=lambda result: result.final_selection_score, reverse=True
        )

        return selection_results[:limit]

    except Exception as error:
        logger.exception("Target selection failed")
        raise TargetSelectionError("Failed To Select Target Exercises.") from error
