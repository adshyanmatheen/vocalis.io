import logging
from io import BytesIO

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly

from app.core.config import settings
from app.domain.audio.exceptions import AudioDecodingError
from app.domain.audio.models import AudioMetadata, ProcessedAudio

logger = logging.getLogger(__name__)


def decode_audio_bytes(audio_bytes: bytes) -> tuple[int, np.ndarray]:

    try:
        waveform, sample_rate = sf.read(
            BytesIO(audio_bytes),
            dtype="float32",
        )

    except Exception as error:
        logger.exception("Audio payload could not be decoded safely")
        raise AudioDecodingError(
            "Audio payload could not be decoded safely."
        ) from error

    return sample_rate, waveform


def convert_to_mono(waveform: np.ndarray) -> np.ndarray:

    if waveform.ndim == 1:
        return waveform

    return np.mean(
        waveform,
        axis=1,
        dtype=np.float32,
    )


def resample_waveform(waveform: np.ndarray, original_sample_rate: int) -> np.ndarray:

    target_sample_rate = settings.app.sample_rate

    if original_sample_rate == target_sample_rate:
        return waveform.astype(np.float32)

    return resample_poly(
        waveform,
        target_sample_rate,
        original_sample_rate,
    ).astype(np.float32)


def build_processed_audio(
    waveform: np.ndarray, original_sample_rate: int, original_channels: int
) -> ProcessedAudio:

    mono_waveform = convert_to_mono(waveform)

    processed_waveform = resample_waveform(
        mono_waveform,
        original_sample_rate,
    )

    metadata = AudioMetadata(
        original_sample_rate=original_sample_rate,
        processed_sample_rate=settings.app.sample_rate,
        original_channels=original_channels,
        processed_channels=1,
        num_samples=int(processed_waveform.shape[0]),
        duration_seconds=float(processed_waveform.shape[0] / settings.app.sample_rate),
    )

    return ProcessedAudio(
        waveform=processed_waveform,
        metadata=metadata,
    )
