from __future__ import annotations

import logging

import numpy as np

from app.domain.phoneme.constants import DEFAULT_MATCH_OVERLAP_THRESHOLD
from app.domain.phoneme.exceptions import PhonemeMatchingError
from app.domain.phoneme.models import (
    ExpectedPhonemeSegment,
    PhonemeMatch,
    PredictedPhonemeSegment,
)

logger = logging.getLogger(__name__)


def build_phoneme_matches(
    expected_segments: list[ExpectedPhonemeSegment],
    predicted_segments: list[PredictedPhonemeSegment],
) -> list[PhonemeMatch]:

    try:
        if not expected_segments or not predicted_segments:
            return []

        expected_starts = np.array([e.start_time for e in expected_segments])
        expected_ends = np.array([e.end_time for e in expected_segments])
        predicted_starts = np.array([p.start_time for p in predicted_segments])
        predicted_ends = np.array([p.end_time for p in predicted_segments])

        overlap_start = np.maximum(expected_starts[:, None], predicted_starts[None, :])
        overlap_end = np.minimum(expected_ends[:, None], predicted_ends[None, :])
        overlap_duration = np.maximum(0, overlap_end - overlap_start)
        expected_duration = np.maximum(0.0001, expected_ends - expected_starts)
        overlap_matrix = overlap_duration / expected_duration[:, None]

        best_match_indices = np.argmax(overlap_matrix, axis=1)
        best_overlap_scores = np.max(overlap_matrix, axis=1)

        matches: list[PhonemeMatch] = []
        for i, expected_segment in enumerate(expected_segments):
            if best_overlap_scores[i] < DEFAULT_MATCH_OVERLAP_THRESHOLD:
                matches.append(
                    PhonemeMatch(
                        expected_phoneme=expected_segment.phoneme,
                        predicted_phoneme="[DELETION]",
                        confidence_score=0.0,
                        overlap_score=0.0,
                        start_time=expected_segment.start_time,
                        end_time=expected_segment.end_time,
                        word=expected_segment.word,
                    )
                )
            else:
                matched = predicted_segments[best_match_indices[i]]
                matches.append(
                    PhonemeMatch(
                        expected_phoneme=expected_segment.phoneme,
                        predicted_phoneme=matched.phoneme,
                        confidence_score=matched.confidence,
                        overlap_score=round(float(best_overlap_scores[i]), 4),
                        start_time=expected_segment.start_time,
                        end_time=expected_segment.end_time,
                        word=expected_segment.word,
                    )
                )

        return matches

    except Exception as error:
        logger.exception("Failed to match expected and predicted phoneme segments")
        raise PhonemeMatchingError(
            "Failed To Match Expected And Predicted Phoneme Segments."
        ) from error
