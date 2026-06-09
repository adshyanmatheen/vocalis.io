from __future__ import annotations

import numpy as np
import pytest

from app.domain.alignment.exceptions import TargetTextNormalizationError
from app.domain.alignment.models import CharacterSegment
from app.domain.alignment.segmenter import (
    extract_character_alignment_segments,
    extract_word_alignment_segments,
)
from app.domain.alignment.tokenizer import (
    encode_alignment_target_text,
    normalize_alignment_target_text,
)
from app.domain.alignment.viterbi import (
    build_extended_alignment_sequence,
    compute_viterbi_alignment_path,
)


class TestTokenizer:
    def test_normalize_lowercases_and_replaces_spaces(self) -> None:
        assert normalize_alignment_target_text("Hello World") == "hello|world"

    def test_normalize_strips_whitespace(self) -> None:
        assert normalize_alignment_target_text("  hello  ") == "hello"

    def test_normalize_raises_on_empty_string(self) -> None:
        with pytest.raises(TargetTextNormalizationError):
            normalize_alignment_target_text("   ")

    def test_encode_valid_text(self) -> None:
        vocabulary = {"h": 0, "e": 1, "l": 2, "o": 3, "|": 4}
        encoded = encode_alignment_target_text("hello", vocabulary)
        assert encoded == [0, 1, 2, 2, 3]

    def test_encode_raises_on_unknown_character(self) -> None:
        vocabulary = {"h": 0, "e": 1}
        with pytest.raises(TargetTextNormalizationError):
            encode_alignment_target_text("hx", vocabulary)


class TestViterbi:
    def test_build_extended_sequence(self) -> None:
        seq = build_extended_alignment_sequence([1, 2, 3], blank_token_id=0)
        assert seq == [0, 1, 0, 2, 0, 3, 0]

    def test_build_extended_sequence_empty(self) -> None:
        seq = build_extended_alignment_sequence([], blank_token_id=0)
        assert seq == [0]

    def test_compute_viterbi_path_single_frame_single_state(self) -> None:
        log_probs = np.array([[0.0, -10.0]], dtype=np.float32)
        path = compute_viterbi_alignment_path(log_probs, [0, 1], blank_token_id=0)
        assert len(path) == 1
        assert path[0] == (0, 0)

    def test_compute_viterbi_path_two_frames(self) -> None:
        log_probs = np.array([[-1.0, -0.5], [-0.8, -0.3]], dtype=np.float32)
        path = compute_viterbi_alignment_path(log_probs, [0, 1], blank_token_id=0)
        assert len(path) == 2
        assert path[1][0] == 1

    def test_compute_viterbi_path_prefers_non_blank_end(self) -> None:
        log_probs = np.array([[-10.0, -0.1], [-10.0, -0.1]], dtype=np.float32)
        path = compute_viterbi_alignment_path(log_probs, [0, 1], blank_token_id=0)
        assert path[-1][1] == 1


class TestSegmenter:
    def test_extract_character_segments_single_character(self) -> None:
        alignment_path = [(0, 1), (1, 1)]
        extended_sequence = [0, 1, 0]
        segments = extract_character_alignment_segments(
            alignment_path=alignment_path,
            extended_sequence=extended_sequence,
            normalized_target_text="A",
            log_probabilities=np.array([[-1.0, -0.5], [-0.5, -0.2]], dtype=np.float32),
            frame_duration_seconds=0.01,
            blank_token_id=0,
        )
        assert len(segments) == 1
        assert segments[0].character == "A"
        assert segments[0].index == 0
        assert segments[0].start_time <= segments[0].end_time

    def test_extract_character_segments_two_characters(self) -> None:
        alignment_path = [(0, 1), (1, 1), (2, 3), (3, 3)]
        extended_sequence = [0, 1, 0, 2, 0]
        segments = extract_character_alignment_segments(
            alignment_path=alignment_path,
            extended_sequence=extended_sequence,
            normalized_target_text="AB",
            log_probabilities=np.full((4, 3), -1.0, dtype=np.float32),
            frame_duration_seconds=0.01,
            blank_token_id=0,
        )
        assert len(segments) == 2
        assert segments[0].character == "A"
        assert segments[1].character == "B"

    def test_extract_character_segments_empty_path(self) -> None:
        segments = extract_character_alignment_segments(
            alignment_path=[],
            extended_sequence=[0],
            normalized_target_text="",
            log_probabilities=np.array([[-1.0]], dtype=np.float32),
            frame_duration_seconds=0.01,
            blank_token_id=0,
        )
        assert segments == []

    def test_extract_word_segments_single_word(self) -> None:
        char_segments = [
            CharacterSegment(
                index=0, character="H", start_time=0.0, end_time=0.1, confidence=0.9
            ),
            CharacterSegment(
                index=1, character="I", start_time=0.1, end_time=0.2, confidence=0.8
            ),
        ]
        word_segments = extract_word_alignment_segments(char_segments)
        assert len(word_segments) == 1
        assert word_segments[0].text == "HI"

    def test_extract_word_segments_multiple_words(self) -> None:
        char_segments = [
            CharacterSegment(
                index=0, character="H", start_time=0.0, end_time=0.1, confidence=0.9
            ),
            CharacterSegment(
                index=1, character="I", start_time=0.1, end_time=0.2, confidence=0.8
            ),
            CharacterSegment(
                index=2, character="|", start_time=0.2, end_time=0.3, confidence=1.0
            ),
            CharacterSegment(
                index=3, character="U", start_time=0.3, end_time=0.4, confidence=0.7
            ),
        ]
        word_segments = extract_word_alignment_segments(char_segments)
        assert len(word_segments) == 2
        assert word_segments[0].text == "HI"
        assert word_segments[1].text == "U"

    def test_extract_word_segments_empty(self) -> None:
        assert extract_word_alignment_segments([]) == []
