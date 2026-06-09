from __future__ import annotations

import logging

from app.domain.phoneme.constants import (
    EXPECTED_PHONEME_SOURCE,
    MINIMUM_WORD_DURATION_SECONDS,
)
from app.domain.phoneme.exceptions import PhonemeSegmentationError
from app.domain.phoneme.models import ExpectedPhonemeSegment
from app.domain.phoneme.phonemizer import phonemize_text

logger = logging.getLogger(__name__)


def estimate_phoneme_duration(word_duration: float, num_phonemes: int) -> float:
    if num_phonemes <= 0:
        return 0.0

    return max(word_duration / num_phonemes, MINIMUM_WORD_DURATION_SECONDS)


def build_expected_phoneme_segments(
    target_text: str, word_segments: list[dict]
) -> list[ExpectedPhonemeSegment]:

    try:
        phoneme_segments: list[ExpectedPhonemeSegment] = []

        for word_segment in word_segments:
            word_text = word_segment.get("text", word_segment.get("word", ""))
            if not word_text:
                continue

            phoneme_words = phonemize_text(word_text)
            if not phoneme_words:
                continue

            phonemes = phoneme_words[0]
            if not phonemes:
                continue

            word_start_time = float(word_segment["start_time"])
            word_end_time = float(word_segment["end_time"])

            word_duration = max(0.0, word_end_time - word_start_time)

            phoneme_duration = estimate_phoneme_duration(word_duration, len(phonemes))

            for phoneme_index, phoneme in enumerate(phonemes):
                start_time = word_start_time + (phoneme_index * phoneme_duration)

                end_time = (
                    word_end_time
                    if phoneme_index == len(phonemes) - 1
                    else (word_start_time + ((phoneme_index + 1) * phoneme_duration))
                )

                phoneme_segments.append(
                    ExpectedPhonemeSegment(
                        word=word_text,
                        phoneme=phoneme,
                        start_time=round(start_time, 4),
                        end_time=round(end_time, 4),
                        source=EXPECTED_PHONEME_SOURCE,
                    )
                )

        return phoneme_segments

    except Exception as error:
        logger.exception("Failed to build expected phoneme segments")
        raise (
            PhonemeSegmentationError("Failed To Build Expected Phoneme Segments.")
        ) from error
