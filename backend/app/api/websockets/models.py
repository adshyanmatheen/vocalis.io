from __future__ import annotations

from collections import deque
from datetime import datetime
from typing import Any

import numpy as np
from msgspec import Struct


class AudioChunkPayload(Struct, kw_only=True):
    type: str
    audio: str
    sequence: int
    sample_rate: int


class IncomingMessageMetadata(Struct, kw_only=True):
    type: str
    sequence: int | None
    sample_rate: int | None
    received_at: str
    validation_status: str
    processing_status: str
    error_message: str | None = None


class RealtimeAssessmentSession(Struct, kw_only=True):
    user_id: int
    target_text: str
    sample_rate: int
    audio_buffer: deque[np.ndarray]
    buffered_samples: int
    received_samples: int
    partial_transcript: str
    last_activity: datetime
    started_at: datetime
    processed_samples: int
    last_sequence: int | None
    inference_in_progress: bool
    inference_task: Any | None
    inference_error: str | None
    message_metadata: list[IncomingMessageMetadata]
    scoring_windows: list[dict[str, Any]]
