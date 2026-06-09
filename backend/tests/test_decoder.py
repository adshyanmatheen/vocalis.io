from __future__ import annotations

import base64

import numpy as np
import pytest

from app.api.websockets.decoder import decode_pcm16_audio_chunk


def test_decode_pcm16_chunk() -> None:
    waveform = np.array([0, 1000, -1000], dtype=np.int16)
    encoded_audio = base64.b64encode(waveform.tobytes()).decode()

    decoded_waveform = decode_pcm16_audio_chunk(encoded_audio)

    assert decoded_waveform.dtype == np.float32
    assert len(decoded_waveform) == 3
    assert decoded_waveform[0] == 0.0


def test_invalid_audio_chunk() -> None:
    with pytest.raises(ValueError):
        decode_pcm16_audio_chunk("invalid")
