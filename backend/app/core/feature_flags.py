from __future__ import annotations

import json
import logging
from datetime import UTC, datetime

from app.core.redis import redis_client

logger = logging.getLogger(__name__)

FEATURE_FLAG_PREFIX = "feature_flag:"
DEFAULT_TTL = 86400


class FeatureFlagService:
    def __init__(self) -> None:
        self._local_cache: dict[str, bool] = {}

    async def is_enabled(self, flag: str, default: bool = False) -> bool:
        if flag in self._local_cache:
            return self._local_cache[flag]

        value = await redis_client.get(f"{FEATURE_FLAG_PREFIX}{flag}")
        if value is None:
            return default

        try:
            parsed = json.loads(value)
            enabled = bool(parsed.get("enabled", default))
            self._local_cache[flag] = enabled
            return enabled
        except json.JSONDecodeError, TypeError:
            return default

    async def set_enabled(
        self, flag: str, enabled: bool, ttl_seconds: int | None = None
    ) -> None:
        payload = json.dumps(
            {
                "enabled": enabled,
                "updated_at": datetime.now(UTC).isoformat(),
            }
        )
        key = f"{FEATURE_FLAG_PREFIX}{flag}"
        await redis_client.setex(key, ttl_seconds or DEFAULT_TTL, payload)
        self._local_cache.pop(flag, None)

    def invalidate_cache(self, flag: str | None = None) -> None:
        if flag:
            self._local_cache.pop(flag, None)
        else:
            self._local_cache.clear()


feature_flags = FeatureFlagService()
