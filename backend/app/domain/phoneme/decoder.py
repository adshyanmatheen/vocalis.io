from __future__ import annotations

import logging

import torch

from app.domain.phoneme.constants import (
    IGNORED_PHONEME_TOKENS,
    PHONEME_TIMESTAMP_PRECISION,
    PREDICTED_PHONEME_SOURCE,
)
from app.domain.phoneme.exceptions import PhonemeDecodingError
from app.domain.phoneme.models import PhonemeModelBundle, PredictedPhonemeSegment

logger = logging.getLogger(__name__)


def extract_predicted_phoneme_segments(
    *,
    logits: torch.Tensor,
    audio_duration_seconds: float,
    model_bundle: PhonemeModelBundle,
) -> list[PredictedPhonemeSegment]:

    try:
        log_probabilities = torch.log_softmax(logits, dim=-1)

        predicted_token_ids = torch.argmax(logits, dim=-1).squeeze(0)

        num_frames = predicted_token_ids.size(0)
        frame_duration = audio_duration_seconds / num_frames if num_frames > 0 else 0.0

        collapsed: list[tuple[int, int, int]] = []
        previous_token_id: int | None = None
        range_start = 0

        for frame_index in range(num_frames):
            token_id = int(predicted_token_ids[frame_index].item())
            if token_id != previous_token_id:
                if previous_token_id is not None:
                    collapsed.append((previous_token_id, range_start, frame_index))
                range_start = frame_index
                previous_token_id = token_id

        if previous_token_id is not None:
            collapsed.append((previous_token_id, range_start, num_frames))

        predicted_segments: list[PredictedPhonemeSegment] = []

        for token_id, range_start, range_end in collapsed:
            decoded = model_bundle.tokenizer.decode([token_id]).strip()

            if not decoded or decoded in IGNORED_PHONEME_TOKENS:
                continue

            frame_probs = log_probabilities[0, range_start:range_end, :]
            max_log_prob = torch.max(frame_probs).item()
            confidence = float(torch.exp(torch.tensor(max_log_prob)))

            start_time = range_start * frame_duration
            end_time = range_end * frame_duration

            predicted_segments.append(
                PredictedPhonemeSegment(
                    phoneme=decoded,
                    start_time=round(start_time, PHONEME_TIMESTAMP_PRECISION),
                    end_time=round(end_time, PHONEME_TIMESTAMP_PRECISION),
                    confidence=round(confidence, 4),
                    source=PREDICTED_PHONEME_SOURCE,
                )
            )

        return predicted_segments

    except Exception as error:
        logger.exception("Failed to decode predicted phoneme segments")
        raise PhonemeDecodingError(
            "Failed To Decode Predicted Phoneme Segments."
        ) from error
