from __future__ import annotations

import asyncio
from functools import partial

from litestar import post
from litestar.connection import Request
from litestar.exceptions import ClientException

from app.core.rate_limiter import alignment_limiter
from app.domain.alignment.mapper import map_alignment_result_to_schema
from app.domain.alignment.service import AlignmentService
from app.domain.audio.processors import build_processed_audio, decode_audio_bytes
from app.domain.audio.validators import validate_audio_payload, validate_audio_waveform
from app.schemas.requests.alignment import AlignmentRequestSchema
from app.schemas.responses.alignment import AlignmentResponseSchema


@post(
    "/alignment",
    operation_id="performAlignment",
    summary="Align Audio To Target Text",
    description="This Route Processes Uploaded Audio Bytes By Decoding, Validating, And Normalizing The Waveform, Then Performs Phoneme-Level Alignment Against The Provided Target Text. Returns Detailed Alignment Data Including Phoneme Boundaries And Confidence Scores. Rate Limited To 10 Requests Per 60 Seconds Per IP Address.",
    tags=["Alignment"],
)
async def perform_alignment(
    request: Request,
    data: AlignmentRequestSchema,
) -> AlignmentResponseSchema:

    client_ip = request.client.host if request.client else "unknown"
    rate_limit = await alignment_limiter.check(client_ip)
    request.state.rate_limit = rate_limit
    if rate_limit.remaining <= 0:
        raise ClientException(
            "Too many alignment requests. Please try again later.",
            headers={
                "X-RateLimit-Limit": str(rate_limit.limit),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(rate_limit.reset_at),
            },
        )
    await alignment_limiter.record(client_ip)
    request.state.rate_limit = await alignment_limiter.check(client_ip)

    validate_audio_payload(data.audio_bytes)

    sample_rate, waveform = await asyncio.to_thread(
        decode_audio_bytes, data.audio_bytes
    )

    validate_audio_waveform(waveform=waveform, sample_rate=sample_rate)

    original_channels = 1 if waveform.ndim == 1 else int(waveform.shape[1])

    processed_audio = await asyncio.to_thread(
        partial(
            build_processed_audio,
            waveform=waveform,
            original_sample_rate=sample_rate,
            original_channels=original_channels,
        ),
    )

    alignment_result = await asyncio.to_thread(
        partial(
            AlignmentService.align_target_text,
            processed_audio=processed_audio.waveform,
            target_text=data.target_text,
        ),
    )

    return map_alignment_result_to_schema(alignment_result)
