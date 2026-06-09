from msgspec import Struct


class CharacterSegmentSchema(Struct, frozen=True):
    index: int
    character: str
    start_time: float
    end_time: float
    confidence: float


class WordSegmentSchema(Struct, frozen=True):
    text: str
    start_time: float
    end_time: float
    confidence: float


class AlignmentResponseSchema(Struct, frozen=True):
    normalized_target_text: str
    character_segments: list[CharacterSegmentSchema]
    word_segments: list[WordSegmentSchema]

    inference_device: str
    quantization_backend: str | None
    quantization_precision: str | None
