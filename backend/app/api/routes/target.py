from __future__ import annotations

from litestar import (
    get,
)
from litestar.params import FromQuery

from app.domain.target.service import (
    TargetService,
)
from app.schemas.responses.target import (
    TargetTextResponse,
)

target_service = TargetService()


@get(path="/targets/current", sync_to_thread=False)
def get_current_target(
    focus_phonemes: FromQuery[str | None] = None,
) -> TargetTextResponse:
    phoneme_set = {
        phoneme.strip().upper()
        for phoneme in (focus_phonemes or "").split(",")
        if phoneme.strip()
    }

    if phoneme_set:
        selected_targets = target_service.get_phoneme_focused_targets(
            phonemes=phoneme_set,
            limit=1,
        )
    else:
        selected_targets = target_service.get_random_targets(limit=1)

    if not selected_targets:
        selected_targets = target_service.get_random_targets(limit=1)

    target = selected_targets[0].target

    return TargetTextResponse(
        id=target.id,
        text=target.text,
        difficulty=target.difficulty,
        category=target.category,
        articulation_focus=list(target.articulation_focus),
        word_count=target.word_count,
    )
