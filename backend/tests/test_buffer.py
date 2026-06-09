from __future__ import annotations

from collections import deque

import numpy as np

from app.api.websockets.buffer import (
    append_audio_chunk,
    merge_audio_buffer,
    trim_processed_audio,
)


def test_append_chunk() -> None:
    audio_buffer = deque()
    audio_chunk = np.array([1, 2, 3], dtype=np.float32)

    append_audio_chunk(audio_buffer=audio_buffer, chunk=audio_chunk)

    assert len(audio_buffer) == 1


def test_merge_buffer() -> None:
    audio_buffer = deque()

    append_audio_chunk(
        audio_buffer=audio_buffer,
        chunk=np.array([1, 2], dtype=np.float32),
    )
    append_audio_chunk(
        audio_buffer=audio_buffer,
        chunk=np.array([3, 4], dtype=np.float32),
    )

    merged_audio = merge_audio_buffer(audio_buffer=audio_buffer)

    assert len(merged_audio) == 4
    assert merged_audio.tolist() == [1.0, 2.0, 3.0, 4.0]


def test_trim_processed_audio() -> None:
    audio_buffer = deque()
    append_audio_chunk(
        audio_buffer=audio_buffer, chunk=np.array([1, 2], dtype=np.float32)
    )
    append_audio_chunk(
        audio_buffer=audio_buffer, chunk=np.array([3, 4], dtype=np.float32)
    )

    trim_processed_audio(audio_buffer=audio_buffer, processed_samples=3)

    assert merge_audio_buffer(audio_buffer=audio_buffer).tolist() == [4.0]
