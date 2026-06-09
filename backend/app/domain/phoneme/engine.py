from __future__ import annotations

import logging
import os
from functools import lru_cache

import torch
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from torchao.quantization import (
    Int8DynamicActivationInt8WeightConfig,
    quantize_,
)
from transformers import (
    Wav2Vec2ForCTC,
    Wav2Vec2PhonemeCTCTokenizer,
    Wav2Vec2Processor,
)

from app.domain.phoneme.constants import (
    PHONEME_MODEL_NAME,
    SUPPORTED_ESPEAK_LIBRARY_PATHS,
)
from app.domain.phoneme.exceptions import (
    PhonemeModelError,
)
from app.domain.phoneme.models import (
    PhonemeModelBundle,
)

logger = logging.getLogger(__name__)


def configure_espeak_environment() -> None:

    if os.environ.get("PHONEMIZER_ESPEAK_LIBRARY"):
        return

    for library_path in SUPPORTED_ESPEAK_LIBRARY_PATHS:
        if os.path.exists(library_path):
            os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = library_path
            EspeakWrapper.set_library(library_path)
            return


def resolve_inference_device() -> torch.device:

    if torch.cuda.is_available():
        return torch.device("cuda")

    if torch.backends.mps.is_available():
        return torch.device("mps")

    return torch.device("cpu")


def apply_model_quantization(model: Wav2Vec2ForCTC) -> Wav2Vec2ForCTC:

    try:
        quantize_(model, Int8DynamicActivationInt8WeightConfig())

    except Exception:
        logger.exception(
            "Failed to quantize phoneme model with Int8DynamicActivationInt8WeightConfig"
        )

    return model


@lru_cache(maxsize=2)
def load_phoneme_model_bundle(*, local_files_only: bool = False) -> PhonemeModelBundle:

    try:
        configure_espeak_environment()
        device = resolve_inference_device()

        tokenizer = Wav2Vec2PhonemeCTCTokenizer.from_pretrained(
            PHONEME_MODEL_NAME,
            local_files_only=local_files_only,
        )
        processor = Wav2Vec2Processor.from_pretrained(
            PHONEME_MODEL_NAME,
            local_files_only=local_files_only,
        )

        model = Wav2Vec2ForCTC.from_pretrained(
            PHONEME_MODEL_NAME,
            local_files_only=local_files_only,
        )
        model = apply_model_quantization(model)
        model = model.to(device)
        model.eval()

        return PhonemeModelBundle(
            processor=processor,
            tokenizer=tokenizer,
            model=model,
            device=device,
        )

    except Exception as error:
        logger.exception("Failed to load phoneme recognition model bundle")
        raise PhonemeModelError(
            "Failed To Load The Phoneme Recognition Model Bundle."
        ) from error
