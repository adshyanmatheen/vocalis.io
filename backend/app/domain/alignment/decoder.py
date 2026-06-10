from typing import Any

import numpy as np
import torch

from app.core.config import settings
from app.domain.alignment.engine import load_alignment_model_bundle
from app.domain.alignment.models import AlignmentResult
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


def perform_forced_alignment(
    processed_audio: np.ndarray, target_text: str
) -> AlignmentResult:

    alignment_bundle = load_alignment_model_bundle()

    normalized_target_text = normalize_alignment_target_text(target_text)

    target_token_ids = encode_alignment_target_text(
        normalized_text=normalized_target_text, vocabulary=alignment_bundle.vocabulary
    )

    inputs: Any = alignment_bundle.processor(
        processed_audio,
        sampling_rate=settings.app.sample_rate,
        return_tensors="pt",
    )

    input_values = inputs.input_values.to(alignment_bundle.inference_device)

    with torch.inference_mode():
        logits = alignment_bundle.model(input_values).logits[0]

    log_probabilities = torch.log_softmax(logits, dim=-1).cpu().numpy()

    extended_sequence = build_extended_alignment_sequence(
        target_token_ids=target_token_ids,
        blank_token_id=alignment_bundle.blank_token_id,
    )

    alignment_path = compute_viterbi_alignment_path(
        log_probabilities=log_probabilities,
        extended_sequence=extended_sequence,
        blank_token_id=alignment_bundle.blank_token_id,
    )

    frame_duration_seconds = float(
        processed_audio.shape[0]
        / settings.app.sample_rate
        / max(1, log_probabilities.shape[0])
    )

    character_segments = extract_character_alignment_segments(
        alignment_path=alignment_path,
        extended_sequence=extended_sequence,
        normalized_target_text=normalized_target_text,
        log_probabilities=log_probabilities,
        frame_duration_seconds=frame_duration_seconds,
        blank_token_id=alignment_bundle.blank_token_id,
    )

    word_segments = extract_word_alignment_segments(character_segments)

    return AlignmentResult(
        normalized_target_text=normalized_target_text,
        character_segments=character_segments,
        word_segments=word_segments,
        inference_device=alignment_bundle.inference_device,
        quantization_backend=alignment_bundle.quantization_backend,
        quantization_precision=alignment_bundle.quantization_precision,
    )
