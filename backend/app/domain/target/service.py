from __future__ import annotations

from app.domain.target.models import (
    TargetSelectionResult,
    TargetText,
)
from app.domain.target.repository import load_target_corpus
from app.domain.target.selector import select_best_targets


class TargetService:
    def __init__(self) -> None:
        self._recent_target_ids: list[str] = []

    def get_all_targets(self) -> tuple[TargetText, ...]:
        return load_target_corpus()

    def select_targets(
        self,
        *,
        focus_phonemes: set[str] | None = None,
        difficulty: str | None = None,
        category: str | None = None,
        limit: int = 5,
    ) -> list[TargetSelectionResult]:

        targets = load_target_corpus()
        selection_results = select_best_targets(
            targets=targets,
            focus_phonemes=focus_phonemes,
            recent_target_ids=self._recent_target_ids,
            difficulty=difficulty,
            category=category,
            limit=limit,
        )

        self._update_recent_history(selection_results)
        return selection_results

    def get_random_targets(
        self,
        *,
        limit: int = 5,
    ) -> list[TargetSelectionResult]:
        return self.select_targets(limit=limit)

    def get_phoneme_focused_targets(
        self, *, phonemes: set[str], difficulty: str | None = None, limit: int = 5
    ) -> list[TargetSelectionResult]:
        return self.select_targets(
            focus_phonemes=phonemes, difficulty=difficulty, limit=limit
        )

    def clear_recent_history(self) -> None:
        self._recent_target_ids.clear()

    def _update_recent_history(
        self, selection_results: list[TargetSelectionResult]
    ) -> None:
        selected_ids = [result.target.id for result in selection_results]
        self._recent_target_ids.extend(selected_ids)
        self._recent_target_ids = self._recent_target_ids[-25:]
