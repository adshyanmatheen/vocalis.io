from __future__ import annotations

from typing import Any

import numpy as np
import torch

from app.domain.phoneme.decoder import (
    extract_predicted_phoneme_segments,
)
from app.domain.phoneme.engine import (
    load_phoneme_model_bundle,
)
from app.domain.phoneme.estimator import build_expected_phoneme_segments
from app.domain.phoneme.matcher import build_phoneme_matches
from app.domain.phoneme.models import (
    ExpectedPhonemeSegment,
    PhonemeMatch,
    PredictedPhonemeSegment,
    ScoringPayload,
)
from app.domain.phoneme.scoring import score_pronunciation


class PhonemeService:
    def estimate_expected_phonemes(
        self, *, target_text: str, word_segments: list[dict[str, Any]]
    ) -> list[ExpectedPhonemeSegment]:
        return build_expected_phoneme_segments(
            target_text=target_text, word_segments=word_segments
        )

    def decode_predicted_phonemes(
        self, *, audio_waveform: np.ndarray, sample_rate: int
    ) -> list[PredictedPhonemeSegment]:
        model_bundle = load_phoneme_model_bundle()
        waveform = np.asarray(audio_waveform, dtype=np.float32)
        audio_duration_seconds = (
            float(waveform.shape[0] / sample_rate) if sample_rate else 0.0
        )

        inputs: Any = model_bundle.processor(
            waveform,
            sampling_rate=sample_rate,
            return_tensors="pt",
            padding=True,
        )
        input_values = inputs.input_values.to(model_bundle.device)

        with torch.no_grad():
            logits = model_bundle.model(input_values).logits

        return extract_predicted_phoneme_segments(
            logits=logits,
            audio_duration_seconds=audio_duration_seconds,
            model_bundle=model_bundle,
        )

    def build_matches(
        self,
        *,
        expected_segments: list[ExpectedPhonemeSegment],
        predicted_segments: list[PredictedPhonemeSegment],
    ) -> list[PhonemeMatch]:
        return build_phoneme_matches(
            expected_segments=expected_segments, predicted_segments=predicted_segments
        )

    def score_matches(self, *, phoneme_matches: list[PhonemeMatch]) -> ScoringPayload:
        return score_pronunciation(phoneme_matches)

    def analyze_pronunciation(
        self,
        *,
        target_text: str,
        word_segments: list[dict[str, Any]],
        audio_waveform: np.ndarray,
        sample_rate: int,
    ) -> ScoringPayload:

        expected_segments = self.estimate_expected_phonemes(
            target_text=target_text, word_segments=word_segments
        )
        predicted_segments = self.decode_predicted_phonemes(
            audio_waveform=audio_waveform, sample_rate=sample_rate
        )

        phoneme_matches = self.build_matches(
            expected_segments=expected_segments, predicted_segments=predicted_segments
        )
        return self.score_matches(phoneme_matches=phoneme_matches)
