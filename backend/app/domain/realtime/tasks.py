from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from typing import Any

import msgspec
import numpy as np

from app.api.websockets.events import (
    PartialFeedbackEvent,
)
from app.api.websockets.manager import (
    connection_manager,
)
from app.api.websockets.models import (
    RealtimeAssessmentSession,
)
from app.core.config import settings
from app.domain.realtime.service import (
    realtime_assessment_service,
)

logger = logging.getLogger(__name__)

_realtime_inference_semaphore = asyncio.Semaphore(
    settings.app.max_concurrent_realtime_inferences
)


async def process_realtime_window(
    *,
    waveform: np.ndarray,
    target_text: str,
    sample_rate: int,
):
    async with _realtime_inference_semaphore:
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(
                    realtime_assessment_service.process_audio_window,
                    waveform=waveform,
                    target_text=target_text,
                    sample_rate=sample_rate,
                ),
                timeout=settings.app.realtime_inference_timeout_seconds,
            )
        except TimeoutError as error:
            raise TimeoutError(
                "Realtime inference timed out. Please try a shorter recording."
            ) from error


async def run_realtime_inference(
    *,
    user_id: int,
    session: RealtimeAssessmentSession,
    waveform: np.ndarray,
    on_complete: Callable[[], Awaitable[None]],
) -> None:
    try:
        scoring_payload = await process_realtime_window(
            waveform=waveform,
            target_text=session.target_text,
            sample_rate=session.sample_rate,
        )
        session.scoring_windows.append(msgspec.to_builtins(scoring_payload))
        partial_feedback = realtime_assessment_service.build_partial_feedback(
            scoring_payload=scoring_payload,
        )

        await connection_manager.send_json(
            user_id=user_id,
            payload=PartialFeedbackEvent(
                overall_score=partial_feedback["overall_score"],
                weak_phonemes=partial_feedback["weak_phonemes"],
                word_scores=partial_feedback["word_scores"],
                performance_band=partial_feedback["performance_band"],
            ),
        )

    except Exception as error:
        logger.exception("Realtime inference task failed for user %d", user_id)
        session.inference_error = str(error)

    finally:
        session.inference_in_progress = False
        session.inference_task = None
        await on_complete()


def schedule_realtime_inference(
    *,
    user_id: int,
    session: RealtimeAssessmentSession,
    waveform: np.ndarray,
    on_complete: Callable[[], Awaitable[None]],
) -> asyncio.Task[Any] | None:
    if session.inference_in_progress:
        return None

    if not session.target_text:
        return None

    task = asyncio.create_task(
        run_realtime_inference(
            user_id=user_id,
            session=session,
            waveform=waveform,
            on_complete=on_complete,
        )
    )
    session.inference_task = task
    session.inference_in_progress = True

    return task
