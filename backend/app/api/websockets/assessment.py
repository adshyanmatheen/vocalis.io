from __future__ import annotations

import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

import msgspec
import numpy as np
from litestar import WebSocket, websocket
from litestar.exceptions import (
    NotAuthorizedException,
    WebSocketDisconnect,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.websockets.auth import (
    authenticate_websocket_user,
)
from app.api.websockets.buffer import (
    append_audio_chunk,
    copy_audio_window,
    merge_audio_buffer,
    trim_processed_audio,
)
from app.api.websockets.decoder import (
    decode_pcm16_audio_chunk,
)
from app.api.websockets.events import (
    AssessmentCompletedEvent,
    AssessmentErrorEvent,
    AssessmentStartedEvent,
)
from app.api.websockets.manager import (
    connection_manager,
)
from app.api.websockets.models import (
    IncomingMessageMetadata,
    RealtimeAssessmentSession,
)
from app.api.websockets.rate_limiter import (
    assessment_rate_limiter,
)
from app.core.config import (
    settings,
)
from app.domain.models import (
    model_readiness_error_message,
    models_are_ready,
)
from app.domain.phoneme.utils import extract_weak_phonemes
from app.domain.realtime.persistence import (
    store_realtime_assessment,
)
from app.domain.realtime.service import (
    realtime_assessment_service,
)
from app.domain.realtime.tasks import (
    process_realtime_window,
    schedule_realtime_inference,
)
from app.domain.utils import normalize_datetime

logger = logging.getLogger(__name__)

DEFAULT_REALTIME_SAMPLE_RATE = 16_000
REALTIME_WINDOW_SECONDS = 2.0
MAX_REALTIME_CHUNK_SECONDS = 1.25
MAX_REALTIME_TARGET_TEXT_CHARS = 240
MIN_REALTIME_AUDIO_SECONDS = 0.35


def capture_message_metadata(
    *,
    session: RealtimeAssessmentSession,
    message: dict[str, Any],
    validation_status: str,
    processing_status: str,
    error_message: str | None = None,
) -> None:
    session.message_metadata.append(
        IncomingMessageMetadata(
            type=str(message.get("type", "unknown")),
            sequence=message.get("sequence")
            if isinstance(message.get("sequence"), int)
            else None,
            sample_rate=message.get("sample_rate")
            if isinstance(message.get("sample_rate"), int)
            else None,
            received_at=datetime.now(UTC).isoformat(),
            validation_status=validation_status,
            processing_status=processing_status,
            error_message=error_message,
        )
    )


async def send_error(*, user_id: int, message: str) -> None:
    await connection_manager.send_json(
        user_id=user_id,
        payload=AssessmentErrorEvent(
            message=message,
        ),
    )


async def maybe_schedule_window(
    *, user_id: int, session: RealtimeAssessmentSession
) -> None:
    if session.inference_in_progress:
        return

    window_samples = int(session.sample_rate * REALTIME_WINDOW_SECONDS)

    if session.buffered_samples < window_samples:
        return

    window = copy_audio_window(
        audio_buffer=session.audio_buffer,
        window_samples=window_samples,
    )
    trimmed_samples = trim_processed_audio(
        audio_buffer=session.audio_buffer,
        processed_samples=window_samples,
    )
    session.buffered_samples = max(0, session.buffered_samples - trimmed_samples)
    session.processed_samples += trimmed_samples

    async def mark_window_complete() -> None:
        return None

    session.inference_task = schedule_realtime_inference(
        user_id=user_id,
        session=session,
        waveform=window,
        on_complete=mark_window_complete,
    )


async def handle_start_assessment(
    *, user_id: int, session: RealtimeAssessmentSession, message: dict[str, Any]
) -> None:
    target_text = message.get("target_text")

    if not isinstance(target_text, str) or not target_text.strip():
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="invalid",
            processing_status="rejected",
            error_message="target_text is required.",
        )
        await send_error(user_id=user_id, message="target_text is required.")
        return

    normalized_target_text = target_text.strip()

    if len(normalized_target_text) > MAX_REALTIME_TARGET_TEXT_CHARS:
        error_message = (
            f"target_text must be {MAX_REALTIME_TARGET_TEXT_CHARS} characters or fewer."
        )
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="invalid",
            processing_status="rejected",
            error_message=error_message,
        )
        await send_error(user_id=user_id, message=error_message)
        return

    if not models_are_ready():
        error_message = model_readiness_error_message()
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="valid",
            processing_status="rejected",
            error_message=error_message,
        )
        await send_error(user_id=user_id, message=error_message)
        return

    sample_rate = message.get("sample_rate", DEFAULT_REALTIME_SAMPLE_RATE)

    if sample_rate != DEFAULT_REALTIME_SAMPLE_RATE:
        error_message = f"Realtime assessment requires {DEFAULT_REALTIME_SAMPLE_RATE} Hz PCM16 audio."
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="invalid",
            processing_status="rejected",
            error_message=error_message,
        )
        await send_error(user_id=user_id, message=error_message)
        return

    session.target_text = normalized_target_text
    session.sample_rate = sample_rate
    session.audio_buffer.clear()
    session.buffered_samples = 0
    session.received_samples = 0
    session.partial_transcript = ""
    session.last_activity = normalize_datetime(datetime.now(UTC))
    session.started_at = normalize_datetime(datetime.now(UTC))
    session.processed_samples = 0
    session.last_sequence = None
    session.inference_in_progress = False
    session.inference_task = None
    session.inference_error = None
    session.message_metadata.clear()
    session.scoring_windows.clear()

    capture_message_metadata(
        session=session,
        message=message,
        validation_status="valid",
        processing_status="started",
    )

    await connection_manager.send_json(
        user_id=user_id,
        payload=AssessmentStartedEvent(
            target_text=session.target_text,
            sample_rate=session.sample_rate,
        ),
    )


async def handle_audio_chunk(
    *, user_id: int, session: RealtimeAssessmentSession, message: dict[str, Any]
) -> None:
    if not session.target_text:
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="invalid",
            processing_status="rejected",
            error_message="start_assessment must be sent before audio_chunk.",
        )
        await send_error(
            user_id=user_id, message="start_assessment must be sent before audio_chunk."
        )
        return

    sequence = message.get("sequence")
    sample_rate = message.get("sample_rate")
    audio = message.get("audio")

    if (
        not isinstance(sequence, int)
        or not isinstance(sample_rate, int)
        or not isinstance(audio, str)
    ):
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="invalid",
            processing_status="rejected",
            error_message="audio_chunk requires audio, sequence, and sample_rate.",
        )
        await send_error(
            user_id=user_id,
            message="audio_chunk requires audio, sequence, and sample_rate.",
        )
        return

    if sample_rate != session.sample_rate:
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="invalid",
            processing_status="rejected",
            error_message="audio_chunk sample_rate does not match the active session.",
        )
        await send_error(
            user_id=user_id,
            message="audio_chunk sample_rate does not match the active session.",
        )
        return

    expected_sequence = (
        1 if session.last_sequence is None else session.last_sequence + 1
    )
    if sequence != expected_sequence:
        error_message = (
            f"audio_chunk sequence must be {expected_sequence}; received {sequence}."
        )
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="invalid",
            processing_status="rejected",
            error_message=error_message,
        )
        await send_error(user_id=user_id, message=error_message)
        return

    max_base64_chars = (
        int(session.sample_rate * MAX_REALTIME_CHUNK_SECONDS * 2 * 4 / 3) + 8
    )
    if len(audio) > max_base64_chars:
        error_message = (
            f"audio_chunk cannot exceed {MAX_REALTIME_CHUNK_SECONDS:.2f} seconds."
        )
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="invalid",
            processing_status="rejected",
            error_message=error_message,
        )
        await send_error(user_id=user_id, message=error_message)
        return

    try:
        chunk = decode_pcm16_audio_chunk(audio)

    except ValueError as error:
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="invalid",
            processing_status="rejected",
            error_message=str(error),
        )
        await send_error(user_id=user_id, message=str(error))
        return

    max_samples = int(settings.app.max_audio_duration_seconds * session.sample_rate)
    if session.received_samples + int(chunk.shape[0]) > max_samples:
        error_message = f"Realtime audio cannot exceed {settings.app.max_audio_duration_seconds:.0f} seconds."
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="invalid",
            processing_status="rejected",
            error_message=error_message,
        )
        await send_error(user_id=user_id, message=error_message)
        return

    appended_samples = append_audio_chunk(
        audio_buffer=session.audio_buffer,
        chunk=chunk,
    )
    session.buffered_samples += appended_samples
    session.received_samples += appended_samples
    session.last_sequence = sequence
    session.last_activity = normalize_datetime(datetime.now(UTC))

    capture_message_metadata(
        session=session,
        message=message,
        validation_status="valid",
        processing_status="buffered",
    )

    await maybe_schedule_window(user_id=user_id, session=session)


async def handle_end_assessment(
    *,
    user_id: int,
    session: RealtimeAssessmentSession,
    message: dict[str, Any],
    database_session: AsyncSession,
) -> None:
    if not session.target_text:
        capture_message_metadata(
            session=session,
            message=message,
            validation_status="invalid",
            processing_status="rejected",
            error_message="No active realtime assessment session.",
        )
        await send_error(
            user_id=user_id, message="No active realtime assessment session."
        )
        return

    capture_message_metadata(
        session=session,
        message=message,
        validation_status="valid",
        processing_status="finalizing",
    )

    waveform = merge_audio_buffer(session.audio_buffer)
    total_samples = session.processed_samples + int(waveform.shape[0])
    duration_seconds = (
        total_samples / session.sample_rate if session.sample_rate else 0.0
    )

    if waveform.size == 0 and not session.scoring_windows:
        await send_error(
            user_id=user_id, message="No audio was received for this assessment."
        )
        return

    try:
        if session.inference_in_progress:
            if session.inference_task is not None:
                await session.inference_task
            else:
                await asyncio.sleep(0)

        if session.inference_error:
            await send_error(user_id=user_id, message=session.inference_error)
            return

        if duration_seconds < MIN_REALTIME_AUDIO_SECONDS:
            await send_error(
                user_id=user_id,
                message="Recording is too short. Please say the full phrase clearly.",
            )
            return

        if waveform.size > 0:
            scoring_payload = await realtime_assessment_service_process(
                waveform=waveform,
                target_text=session.target_text,
                sample_rate=session.sample_rate,
            )
            session.scoring_windows.append(msgspec.to_builtins(scoring_payload))

        scoring_payload = realtime_assessment_service.aggregate_scoring_windows(
            scoring_windows=session.scoring_windows,
        )
        feedback = realtime_assessment_service.build_completion_feedback(
            scoring_payload=scoring_payload,
            duration_seconds=duration_seconds,
        )
        weak_phonemes = extract_weak_phonemes(
            phoneme_results=scoring_payload["phoneme_results"],
        )

        await asyncio.gather(
            store_realtime_assessment(
                database_session=database_session,
                user_id=user_id,
                target_text=session.target_text,
                scoring_payload=scoring_payload,
                duration_seconds=duration_seconds,
                message_metadata=session.message_metadata,
            ),
            connection_manager.send_json(
                user_id=user_id,
                payload=AssessmentCompletedEvent(
                    overall_score=scoring_payload["overall_score"],
                    performance_band=scoring_payload["performance_band"],
                    feedback=feedback,
                    weak_phonemes=weak_phonemes,
                    word_scores=msgspec.to_builtins(scoring_payload["word_scores"]),
                ),
            ),
        )

    except Exception as error:
        logger.exception("End assessment failed for user %d", user_id)
        await send_error(user_id=user_id, message=str(error))

    finally:
        session.audio_buffer.clear()
        connection_manager.disconnect(user_id=user_id)


async def realtime_assessment_service_process(
    *, waveform: np.ndarray, target_text: str, sample_rate: int
):
    return await process_realtime_window(
        waveform=waveform,
        target_text=target_text,
        sample_rate=sample_rate,
    )


@websocket(path="/ws/assessment")
async def assessment_websocket_handler(
    socket: WebSocket, database_session: AsyncSession
) -> None:
    user_id: int | None = None

    try:
        user = await authenticate_websocket_user(
            websocket=socket,
            database_session=database_session,
        )
        user_id = user.id

        if assessment_rate_limiter.is_rate_limited(user_id=user_id):
            await socket.send_json(
                AssessmentErrorEvent(
                    message="Rate limit exceeded. Maximum 10 assessments per minute.",
                )
            )
            await socket.close(code=1008, reason="Rate limited")
            return

        assessment_rate_limiter.record_attempt(user_id=user_id)
        session = await connection_manager.connect(
            websocket=socket,
            user_id=user_id,
            sample_rate=DEFAULT_REALTIME_SAMPLE_RATE,
        )

    except NotAuthorizedException:
        await socket.close(code=1008)
        return

    try:
        while True:
            message = await socket.receive_json()

            if not isinstance(message, dict):
                await send_error(
                    user_id=user_id, message="WebSocket message must be a JSON object."
                )
                continue

            message_type = message.get("type")

            if message_type == "start_assessment":
                await handle_start_assessment(
                    user_id=user_id,
                    session=session,
                    message=message,
                )
                continue

            if message_type == "audio_chunk":
                await handle_audio_chunk(
                    user_id=user_id,
                    session=session,
                    message=message,
                )
                continue

            if message_type == "end_assessment":
                await handle_end_assessment(
                    user_id=user_id,
                    session=session,
                    message=message,
                    database_session=database_session,
                )
                return

            capture_message_metadata(
                session=session,
                message=message,
                validation_status="invalid",
                processing_status="rejected",
                error_message="Unsupported realtime message type.",
            )
            await send_error(
                user_id=user_id, message="Unsupported realtime message type."
            )

    except WebSocketDisconnect:
        pass

    finally:
        if user_id is not None:
            connection_manager.disconnect(user_id=user_id)
