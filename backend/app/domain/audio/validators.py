import numpy as np

from app.core.config import settings
from app.domain.audio.constants import SUPPORTED_AUDIO_DIMENSIONS
from app.domain.audio.exceptions import AudioValidationError


def validate_audio_payload(audio_bytes: bytes) -> None:

    if not audio_bytes:
        raise AudioValidationError(
            "The Audio Payload Is Empty. Please Provide Valid Audio Recordings."
        )

    max_payload_size = settings.app.max_websocket_buffer_mb * 1024 * 1024

    if len(audio_bytes) > max_payload_size:
        raise AudioValidationError(
            f"The Audio Payload Exceeds The Maximum Allowed Size Of {settings.app.max_websocket_buffer_mb} MB. Please Provide Smaller Audio Recordings."
        )


def validate_audio_waveform(waveform: np.ndarray, sample_rate: int) -> None:

    if sample_rate <= 0:
        raise AudioValidationError(
            "The Sample Rate Must Be A Positive Valid Integer. Please Provide A Valid Sample Rate."
        )

    if waveform.size == 0:
        raise AudioValidationError(
            "The Audio Waveform Is Empty. Please Provide Valid Audio Recordings."
        )

    if waveform.ndim > SUPPORTED_AUDIO_DIMENSIONS:
        raise AudioValidationError(
            f"The Audio Waveform Has More Than {SUPPORTED_AUDIO_DIMENSIONS} Dimensions. Please Provide Valid Mono Or Stereo Audio Recordings."
        )

    num_samples = int(waveform.shape[0])

    duration_seconds = num_samples / sample_rate

    if duration_seconds < settings.app.min_audio_duration_seconds:
        raise AudioValidationError(
            f"The Audio Duration Is Too Short. Minimum Duration Is {settings.app.min_audio_duration_seconds} Seconds. Please Provide Longer Audio Recordings."
        )

    if duration_seconds > settings.app.max_audio_duration_seconds:
        raise AudioValidationError(
            f"The Audio Duration Is Too Long. Maximum Duration Is {settings.app.max_audio_duration_seconds} Seconds. Please Provide Shorter Audio Recordings."
        )
