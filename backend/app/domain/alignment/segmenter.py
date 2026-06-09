import numpy as np

from app.domain.alignment.constants import DEFAULT_ALIGNMENT_WORD_DELIMITER
from app.domain.alignment.models import CharacterSegment, WordSegment


def extract_character_alignment_segments(
    alignment_path: list[tuple[int, int]],
    extended_sequence: list[int],
    normalized_target_text: str,
    log_probabilities: np.ndarray,
    frame_duration_seconds: float,
    blank_token_id: int,
) -> list[CharacterSegment]:

    character_segments: list[CharacterSegment] = []

    current_character_index: int | None = None
    current_start_time = 0.0
    current_end_time = 0.0

    confidence_values: list[float] = []

    for frame_index, state_index in alignment_path:
        token_id = extended_sequence[state_index]

        if token_id == blank_token_id or state_index % 2 == 0:
            current_character_index = None
            continue

        character_index = (state_index - 1) // 2

        confidence = float(np.exp(log_probabilities[frame_index, token_id]))

        if current_character_index == character_index:
            current_end_time = (frame_index + 1) * frame_duration_seconds
            confidence_values.append(confidence)
            continue

        if current_character_index is not None:
            character_segments.append(
                CharacterSegment(
                    index=current_character_index,
                    character=normalized_target_text[current_character_index],
                    start_time=current_start_time,
                    end_time=current_end_time,
                    confidence=float(sum(confidence_values) / len(confidence_values)),
                )
            )

        current_character_index = character_index
        current_start_time = frame_index * frame_duration_seconds
        current_end_time = (frame_index + 1) * frame_duration_seconds
        confidence_values = [confidence]

    if current_character_index is not None:
        character_segments.append(
            CharacterSegment(
                index=current_character_index,
                character=normalized_target_text[current_character_index],
                start_time=current_start_time,
                end_time=current_end_time,
                confidence=float(sum(confidence_values) / len(confidence_values)),
            )
        )

    return character_segments


def extract_word_alignment_segments(
    character_segments: list[CharacterSegment],
) -> list[WordSegment]:

    word_segments: list[WordSegment] = []
    current_word_characters: list[str] = []

    current_word_start_time: float | None = None
    current_word_end_time: float | None = None

    current_word_confidences: list[float] = []

    for segment in character_segments:
        if segment.character == DEFAULT_ALIGNMENT_WORD_DELIMITER:
            if current_word_characters:
                word_segments.append(
                    WordSegment(
                        text="".join(current_word_characters),
                        start_time=current_word_start_time or 0.0,
                        end_time=current_word_end_time or 0.0,
                        confidence=float(
                            sum(current_word_confidences)
                            / len(current_word_confidences)
                        ),
                    )
                )

            current_word_characters = []
            current_word_start_time = None
            current_word_end_time = None
            current_word_confidences = []

            continue

        if current_word_start_time is None:
            current_word_start_time = segment.start_time

        current_word_characters.append(segment.character)
        current_word_end_time = segment.end_time
        current_word_confidences.append(segment.confidence)

    if current_word_characters:
        word_segments.append(
            WordSegment(
                text="".join(current_word_characters),
                start_time=current_word_start_time or 0.0,
                end_time=current_word_end_time or 0.0,
                confidence=float(
                    sum(current_word_confidences) / len(current_word_confidences)
                ),
            )
        )

    return word_segments
