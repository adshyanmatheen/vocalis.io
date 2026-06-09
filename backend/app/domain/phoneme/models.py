from __future__ import annotations

from enum import (
    StrEnum,
)
from typing import TypedDict

import torch
from msgspec import Struct
from transformers import Wav2Vec2ForCTC, Wav2Vec2PhonemeCTCTokenizer, Wav2Vec2Processor


class Severity(StrEnum):
    NONE = "none"
    MILD = "mild"
    MODERATE = "moderate"
    SEVERE = "severe"


class ErrorType(StrEnum):
    NONE = "none"
    SUBSTITUTION = "substitution"
    DISTORTION = "distortion"
    DELETION = "deletion"
    INSERTION = "insertion"


class PerformanceBand(StrEnum):
    EXCELLENT = "Excellent"
    STRONG = "Strong"
    ON_TRACK = "On Track"
    NEEDS_MORE_PRACTICE = "Needs More Practice"
    NEEDS_CAREFUL_PRACTICE = "Needs Careful Practice"


class PhonemeModelBundle(Struct, frozen=True):
    processor: Wav2Vec2Processor
    tokenizer: Wav2Vec2PhonemeCTCTokenizer
    model: Wav2Vec2ForCTC
    device: torch.device


class ExpectedPhonemeSegment(Struct, frozen=True):
    word: str
    phoneme: str
    start_time: float
    end_time: float
    source: str


class PredictedPhonemeSegment(Struct, frozen=True):
    phoneme: str
    start_time: float
    end_time: float
    confidence: float
    source: str


class PhonemeMatch(Struct, frozen=True):
    expected_phoneme: str
    predicted_phoneme: str
    confidence_score: float
    overlap_score: float
    start_time: float
    end_time: float
    word: str


class PronunciationDiagnosis(Struct, frozen=True):
    expected_phoneme: str
    predicted_phoneme: str
    confidence_score: float
    severity: str
    start_time: float
    end_time: float
    word: str
    source: str


class ScoredPhonemeResult(TypedDict):
    expected_phoneme: str
    predicted_phoneme: str
    confidence_score: float
    overlap_score: float
    start_time: float
    end_time: float
    word: str
    severity: str
    error_type: str
    severity_score: float
    importance_weight: float
    phoneme_score: float


class WordScore(TypedDict):
    word: str
    weighted_score: float
    average_confidence: float
    phoneme_count: int
    performance_band: str


class ScoringPayload(TypedDict):
    phoneme_results: list[ScoredPhonemeResult]
    word_scores: list[WordScore]
    overall_score: float
    performance_band: str


class WordSegment(Struct, frozen=True):
    word: str
    start_time: float
    end_time: float
    confidence: float
