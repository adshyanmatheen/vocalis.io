from __future__ import annotations

from datetime import UTC, datetime


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)

    return value
