from __future__ import annotations

from pydantic import BaseModel


class TargetTextResponse(BaseModel):
    id: str
    text: str
    difficulty: str
    category: str
    articulation_focus: list[str]
    word_count: int
