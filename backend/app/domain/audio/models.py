from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True, slots=True)
class AudioMetadata:
    original_sample_rate: int
    processed_sample_rate: int
    original_channels: int
    processed_channels: int
    num_samples: int
    duration_seconds: float


@dataclass(frozen=True, slots=True)
class ProcessedAudio:
    waveform: np.ndarray
    metadata: AudioMetadata
