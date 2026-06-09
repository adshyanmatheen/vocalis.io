from __future__ import annotations

import pytest

from app.domain.target.constants import (
    DEFAULT_PHONEME_MATCH_SCORE,
)
from app.domain.target.exceptions import (
    TargetRepositoryError,
    TargetValidationError,
)
from app.domain.target.models import TargetSelectionResult, TargetText
from app.domain.target.repository import (
    build_phoneme_inventory,
    build_target_text,
    infer_articulation_focus,
    load_target_corpus,
    normalize_target_text,
    validate_target_data,
)
from app.domain.target.selector import (
    compute_difficulty_score,
    compute_phoneme_match_score,
    compute_recency_penalty,
    compute_selection_score,
    filter_targets,
    select_best_targets,
)


def _make_target(**overrides: object) -> TargetText:
    defaults = dict(
        id="t1",
        text="hello world",
        difficulty="easy",
        category="general",
        phonemes=(("HH", "EH", "L", "OW"), ("W", "ER", "L", "D")),
        phoneme_inventory=frozenset({"HH", "EH", "L", "OW", "W", "ER", "D"}),
        articulation_focus=(),
        word_count=2,
    )
    defaults.update(overrides)
    return TargetText(**defaults)


class TestComputePhonemeMatchScore:
    def test_full_match(self) -> None:
        target = _make_target()
        score = compute_phoneme_match_score(target, {"HH", "EH", "L"})
        assert score == pytest.approx(1.0)

    def test_partial_match(self) -> None:
        target = _make_target()
        score = compute_phoneme_match_score(target, {"HH", "ZZ"})
        assert score == pytest.approx(0.5)

    def test_no_match(self) -> None:
        target = _make_target()
        score = compute_phoneme_match_score(target, {"ZZ", "XX"})
        assert score == pytest.approx(0.0)

    def test_empty_focus_phonemes_returns_default(self) -> None:
        target = _make_target()
        score = compute_phoneme_match_score(target, set())
        assert score == DEFAULT_PHONEME_MATCH_SCORE


class TestComputeDifficultyScore:
    def test_matches_preferred(self) -> None:
        target = _make_target(difficulty="medium")
        assert compute_difficulty_score(target, "medium") == 1.0

    def test_does_not_match_preferred(self) -> None:
        target = _make_target(difficulty="easy")
        assert compute_difficulty_score(target, "hard") == 0.5


class TestComputeRecencyPenalty:
    def test_not_in_history(self) -> None:
        target = _make_target(id="t1")
        assert compute_recency_penalty(target, ["t2", "t3"]) == 0.0

    def test_in_history(self) -> None:
        target = _make_target(id="t1")
        penalty = compute_recency_penalty(target, ["t2", "t1", "t3"])
        assert penalty > 0.0

    def test_most_recent_gets_lower_penalty(self) -> None:
        target = _make_target(id="t1")
        penalty_recent = compute_recency_penalty(target, ["t2", "t1"])
        penalty_older = compute_recency_penalty(target, ["t1", "t2"])
        assert penalty_recent < penalty_older


class TestComputeSelectionScore:
    def test_basic_score(self) -> None:
        score = compute_selection_score(
            phoneme_match_score=0.8, difficulty_score=1.0, recency_penalty_score=0.1
        )
        expected_base = (0.8 * 0.45) + (1.0 * 0.25) - (0.1 * 0.30)
        assert score >= expected_base
        assert score <= expected_base + 0.15


class TestFilterTargets:
    def test_no_filters(self) -> None:
        t1 = _make_target(id="t1")
        t2 = _make_target(id="t2", difficulty="hard")
        result = filter_targets(targets=(t1, t2), difficulty=None, category=None)
        assert len(result) == 2

    def test_filter_by_difficulty(self) -> None:
        t1 = _make_target(id="t1", difficulty="easy")
        t2 = _make_target(id="t2", difficulty="hard")
        result = filter_targets(targets=(t1, t2), difficulty="easy", category=None)
        assert result == [t1]

    def test_filter_by_category(self) -> None:
        t1 = _make_target(id="t1", category="general")
        t2 = _make_target(id="t2", category="academic")
        result = filter_targets(targets=(t1, t2), difficulty=None, category="academic")
        assert result == [t2]

    def test_filter_by_both(self) -> None:
        t1 = _make_target(id="t1", difficulty="easy", category="general")
        t2 = _make_target(id="t2", difficulty="easy", category="academic")
        result = filter_targets(targets=(t1, t2), difficulty="easy", category="general")
        assert result == [t1]

    def test_no_matches(self) -> None:
        t1 = _make_target(id="t1", difficulty="easy")
        result = filter_targets(targets=(t1,), difficulty="hard", category=None)
        assert result == []


class TestSelectBestTargets:
    def test_returns_empty_for_empty_targets(self) -> None:
        assert select_best_targets(targets=()) == []

    def test_returns_limited_results(self) -> None:
        targets = tuple(_make_target(id=f"t{i}") for i in range(20))
        results = select_best_targets(targets=targets, limit=5)
        assert len(results) <= 5

    def test_results_are_target_selection_results(self) -> None:
        targets = (_make_target(),)
        results = select_best_targets(targets=targets)
        assert all(isinstance(r, TargetSelectionResult) for r in results)

    def test_filters_by_difficulty(self) -> None:
        t1 = _make_target(id="t1", difficulty="easy")
        t2 = _make_target(id="t2", difficulty="hard")
        results = select_best_targets(targets=(t1, t2), difficulty="hard")
        assert len(results) == 1
        assert results[0].target.id == "t2"

    def test_sorts_by_score_descending(self) -> None:
        targets = tuple(_make_target(id=f"t{i}") for i in range(5))
        results = select_best_targets(targets=targets, limit=5)
        scores = [r.final_selection_score for r in results]
        assert all(scores[i] >= scores[i + 1] for i in range(len(scores) - 1))


class TestRepository:
    def test_normalize_target_text(self) -> None:
        assert normalize_target_text("  hello   world  ") == "hello world"

    def test_build_phoneme_inventory(self) -> None:
        phonemes = (("HH", "EH"), ("L", "OW"))
        inventory = build_phoneme_inventory(phonemes)
        assert inventory == frozenset({"HH", "EH", "L", "OW"})

    def test_infer_articulation_focus_with_matches(self) -> None:
        inventory = frozenset({"R", "L", "AA", "IH"})
        focus = infer_articulation_focus(inventory)
        assert "R" in focus
        assert "L" in focus

    def test_infer_articulation_focus_no_matches(self) -> None:
        inventory = frozenset({"AA", "IH", "UU"})
        assert infer_articulation_focus(inventory) == ()

    def test_validate_target_data_raises_on_empty_text(self) -> None:
        with pytest.raises(TargetValidationError):
            validate_target_data({"text": "", "difficulty": "easy"})

    def test_validate_target_data_raises_on_invalid_difficulty(self) -> None:
        with pytest.raises(TargetValidationError):
            validate_target_data({"text": "hello", "difficulty": "extreme"})

    def test_validate_target_data_passes_valid(self) -> None:
        validate_target_data({"text": "hello", "difficulty": "easy"})

    def test_build_target_text(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(
            "app.domain.target.repository.phonemize_text",
            lambda text: (("HH", "EH", "L", "OW"),),
        )
        target = build_target_text(
            {"text": "hello", "difficulty": "easy", "category": "general"}, 0
        )
        assert target.id == "target_0"
        assert target.text == "hello"
        assert target.difficulty == "easy"
        assert target.word_count == 1

    def test_load_target_corpus_raises_on_empty(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr("app.domain.target.repository.TARGET_CORPUS", [])
        monkeypatch.setattr(
            "app.domain.target.repository.load_target_corpus",
            lambda: (_ for _ in ()).throw(
                TargetRepositoryError("The Target Corpus Cannot Be Empty.")
            ),
        )
        with pytest.raises(TargetRepositoryError):
            load_target_corpus()
