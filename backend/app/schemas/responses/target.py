from msgspec import Struct


class TargetTextResponse(Struct, kw_only=True):
    id: str
    text: str
    difficulty: str
    category: str
    articulation_focus: list[str]
    word_count: int
