from __future__ import annotations

import base64
import binascii

import numpy as np


def decode_pcm16_audio_chunk(base64_audio: str) -> np.ndarray:
    try:
        audio_bytes = base64.b64decode(base64_audio, validate=True)

    except (binascii.Error, ValueError) as error:
        raise ValueError("Audio Chunk Is Not Valid Base64 PCM16 Data.") from error

    if len(audio_bytes) == 0:
        return np.array([], dtype=np.float32)

    if len(audio_bytes) % 2 != 0:
        raise ValueError("PCM16 Audio Byte Length Must Be Even.")

    pcm_samples = np.frombuffer(audio_bytes, dtype=np.int16)

    return (pcm_samples.astype(np.float32) / 32768.0).clip(-1.0, 1.0)
