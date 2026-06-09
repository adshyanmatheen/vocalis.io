from msgspec import Struct


class AlignmentRequestSchema(Struct, frozen=True):
    audio_bytes: bytes
    target_text: str
