from __future__ import annotations

from msgspec import Struct


class TargetText(Struct, frozen=True):
    id: str
    text: str
    difficulty: str
    category: str
    phonemes: tuple[tuple[str, ...], ...]
    phoneme_inventory: frozenset[str]
    articulation_focus: tuple[str, ...]
    word_count: int


class TargetSelectionResult(Struct, frozen=True):
    target: TargetText
    matched_focus_phonemes: tuple[str, ...]
    phoneme_match_score: float
    difficulty_score: float
    recency_penalty_score: float
    final_selection_score: float
