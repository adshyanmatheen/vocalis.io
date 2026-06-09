from __future__ import annotations

from collections import deque

import numpy as np


def append_audio_chunk(*, audio_buffer: deque[np.ndarray], chunk: np.ndarray) -> int:
    if chunk.size == 0:
        return 0

    normalized_chunk = chunk.astype(np.float32, copy=False)
    audio_buffer.append(normalized_chunk)
    return int(normalized_chunk.shape[0])


def merge_audio_buffer(audio_buffer: deque[np.ndarray]) -> np.ndarray:
    if not audio_buffer:
        return np.array([], dtype=np.float32)

    return np.concatenate(list(audio_buffer)).astype(np.float32, copy=False)


def copy_audio_window(
    *, audio_buffer: deque[np.ndarray], window_samples: int
) -> np.ndarray:
    if window_samples <= 0 or not audio_buffer:
        return np.array([], dtype=np.float32)

    chunks: list[np.ndarray] = []
    remaining_samples = window_samples

    for chunk in audio_buffer:
        if remaining_samples <= 0:
            break

        if chunk.shape[0] <= remaining_samples:
            chunks.append(chunk)
            remaining_samples -= int(chunk.shape[0])
            continue

        chunks.append(chunk[:remaining_samples])
        remaining_samples = 0

    if not chunks:
        return np.array([], dtype=np.float32)

    return np.concatenate(chunks).astype(np.float32, copy=True)


def trim_processed_audio(
    *, audio_buffer: deque[np.ndarray], processed_samples: int
) -> int:
    remaining_to_trim = processed_samples
    trimmed_samples = 0

    while audio_buffer and remaining_to_trim > 0:
        chunk = audio_buffer[0]

        if remaining_to_trim >= chunk.shape[0]:
            remaining_to_trim -= chunk.shape[0]
            trimmed_samples += int(chunk.shape[0])
            audio_buffer.popleft()
            continue

        audio_buffer[0] = chunk[remaining_to_trim:]
        trimmed_samples += remaining_to_trim
        remaining_to_trim = 0

    return trimmed_samples
