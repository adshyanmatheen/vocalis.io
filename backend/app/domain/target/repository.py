from __future__ import annotations

import logging
from functools import lru_cache

from app.domain.phoneme.phonemizer import phonemize_text
from app.domain.target.constants import DEFAULT_TARGET_CATEGORY, TARGET_DIFFICULTIES
from app.domain.target.corpus import TARGET_CORPUS
from app.domain.target.exceptions import TargetRepositoryError, TargetValidationError
from app.domain.target.models import TargetText

logger = logging.getLogger(__name__)


def normalize_target_text(text: str) -> str:
    return " ".join(text.strip().split())


def build_phoneme_inventory(phonemes: tuple[tuple[str, ...], ...]) -> frozenset[str]:
    return frozenset(phoneme.upper() for word in phonemes for phoneme in word)


def infer_articulation_focus(phoneme_inventory: frozenset[str]) -> tuple[str, ...]:
    focus_phonemes = {
        "R",
        "L",
        "TH",
        "DH",
        "SH",
        "CH",
    }
    return tuple(
        sorted(phoneme for phoneme in phoneme_inventory if phoneme in focus_phonemes)
    )


def validate_target_data(target_data: dict) -> None:

    text = normalize_target_text(str(target_data.get("text", "")))
    difficulty = str(target_data.get("difficulty", "")).lower()

    if not text:
        raise TargetValidationError("The Target Text Cannot Be Empty.")

    if difficulty not in TARGET_DIFFICULTIES:
        raise TargetValidationError("The Target Difficulty Is Invalid.")


def build_target_text(target_data: dict, index: int) -> TargetText:
    validate_target_data(target_data)

    text = normalize_target_text(target_data["text"])
    difficulty = target_data["difficulty"].strip().lower()
    category = str(target_data.get("category", DEFAULT_TARGET_CATEGORY)).strip().lower()

    phonemes = tuple(tuple(word) for word in phonemize_text(text))
    phoneme_inventory = build_phoneme_inventory(phonemes)
    articulation_focus = infer_articulation_focus(phoneme_inventory)

    return TargetText(
        id=f"target_{index}",
        text=text,
        difficulty=difficulty,
        category=category,
        phonemes=phonemes,
        phoneme_inventory=phoneme_inventory,
        articulation_focus=articulation_focus,
        word_count=len(text.split()),
    )


@lru_cache(maxsize=1)
def load_target_corpus() -> tuple[TargetText, ...]:
    try:
        if not TARGET_CORPUS:
            raise TargetRepositoryError("The Target Corpus Cannot Be Empty.")

        targets: list[TargetText] = []
        for index, target_data in enumerate(TARGET_CORPUS):
            if not isinstance(target_data, dict):
                continue

            try:
                target = build_target_text(target_data, index)
                targets.append(target)

            except TargetValidationError:
                continue

        if not targets:
            raise TargetRepositoryError(
                "There Are No Valid Target Exercises Were Found."
            )

        return tuple(targets)

    except Exception as error:
        logger.exception("Failed to load the target corpus")
        raise TargetRepositoryError("Failed To Load The Target Corpus.") from error
