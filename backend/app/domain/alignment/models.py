from dataclasses import dataclass

from transformers import AutoModelForCTC, AutoProcessor


@dataclass(frozen=True, slots=True)
class AlignmentModelBundle:
    processor: AutoProcessor
    model: AutoModelForCTC

    blank_token_id: int
    vocabulary: dict[str, int]

    inference_device: str
    quantization_backend: str | None
    quantization_precision: str | None


@dataclass(frozen=True, slots=True)
class CharacterSegment:
    index: int
    character: str

    start_time: float
    end_time: float

    confidence: float


@dataclass(frozen=True, slots=True)
class WordSegment:
    text: str
    start_time: float
    end_time: float
    confidence: float


@dataclass(frozen=True, slots=True)
class AlignmentResult:
    normalized_target_text: str

    character_segments: list[CharacterSegment]
    word_segments: list[WordSegment]

    inference_device: str
    quantization_backend: str | None
    quantization_precision: str | None
