from app.domain.alignment.models import AlignmentResult, CharacterSegment, WordSegment
from app.schemas.responses.alignment import (
    AlignmentResponseSchema,
    CharacterSegmentSchema,
    WordSegmentSchema,
)


def map_character_segment_to_schema(
    segment: CharacterSegment,
) -> CharacterSegmentSchema:

    return CharacterSegmentSchema(
        index=segment.index,
        character=segment.character,
        start_time=segment.start_time,
        end_time=segment.end_time,
        confidence=segment.confidence,
    )


def map_word_segment_to_schema(segment: WordSegment) -> WordSegmentSchema:

    return WordSegmentSchema(
        text=segment.text,
        start_time=segment.start_time,
        end_time=segment.end_time,
        confidence=segment.confidence,
    )


def map_alignment_result_to_schema(result: AlignmentResult) -> AlignmentResponseSchema:

    return AlignmentResponseSchema(
        normalized_target_text=result.normalized_target_text,
        character_segments=[
            map_character_segment_to_schema(segment)
            for segment in result.character_segments
        ],
        word_segments=[
            map_word_segment_to_schema(segment) for segment in result.word_segments
        ],
        inference_device=result.inference_device,
        quantization_backend=result.quantization_backend,
        quantization_precision=result.quantization_precision,
    )
