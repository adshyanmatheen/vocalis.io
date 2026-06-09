from litestar import post

from app.domain.alignment.mapper import map_alignment_result_to_schema
from app.domain.alignment.service import AlignmentService
from app.domain.audio.processors import build_processed_audio, decode_audio_bytes
from app.domain.audio.validators import validate_audio_payload, validate_audio_waveform
from app.schemas.requests.alignment import AlignmentRequestSchema
from app.schemas.responses.alignment import AlignmentResponseSchema


@post("/alignment")
def perform_alignment(data: AlignmentRequestSchema) -> AlignmentResponseSchema:

    validate_audio_payload(data.audio_bytes)

    sample_rate, waveform = decode_audio_bytes(data.audio_bytes)

    validate_audio_waveform(waveform=waveform, sample_rate=sample_rate)

    original_channels = 1 if waveform.ndim == 1 else int(waveform.shape[1])

    processed_audio = build_processed_audio(
        waveform=waveform,
        original_sample_rate=sample_rate,
        original_channels=original_channels,
    )

    alignment_result = AlignmentService.align_target_text(
        processed_audio=processed_audio.waveform,
        target_text=data.target_text,
    )

    return map_alignment_result_to_schema(alignment_result)
