from app.domain.alignment.constants import DEFAULT_ALIGNMENT_WORD_DELIMITER
from app.domain.alignment.exceptions import TargetTextNormalizationError


def normalize_alignment_target_text(target_text: str) -> str:

    normalized_text = (
        target_text.strip().lower().replace(" ", DEFAULT_ALIGNMENT_WORD_DELIMITER)
    )

    if not normalized_text:
        raise TargetTextNormalizationError("The Alignment Target Text Cannot Be Empty.")

    return normalized_text


def encode_alignment_target_text(
    normalized_text: str, vocabulary: dict[str, int]
) -> list[int]:

    try:
        return [vocabulary[character] for character in normalized_text]

    except KeyError as error:
        raise TargetTextNormalizationError(
            f"Unsupported Alignment Character Detected: {error.args[0]}"
        ) from error
