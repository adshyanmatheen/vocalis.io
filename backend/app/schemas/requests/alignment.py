from msgspec import Struct


class AlignmentRequestSchema(Struct, frozen=True):
    audio_bytes: bytes
    target_text: str

    def __post_init__(self) -> None:
        if not self.audio_bytes:
            raise ValueError("audio_bytes is required")
        if not self.target_text.strip():
            raise ValueError("target_text is required")
        if len(self.target_text) > 500:
            raise ValueError("target_text must not exceed 500 characters")
