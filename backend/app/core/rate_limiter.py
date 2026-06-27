from __future__ import annotations

import logging
from datetime import UTC, datetime, timedelta

from app.core.redis import redis_client

logger = logging.getLogger(__name__)


class SlidingWindowRateLimiter:
    def __init__(self, prefix: str, max_attempts: int, window_seconds: int) -> None:
        self._prefix = prefix
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._in_memory: dict[str, list[datetime]] = {}

    def _make_key(self, identifier: str) -> str:
        return f"{self._prefix}:{identifier}"

    async def is_limited(self, identifier: str) -> bool:
        if redis_client.is_connected:
            return await self._is_limited_redis(identifier)
        return self._is_limited_memory(identifier)

    async def record(self, identifier: str) -> None:
        if redis_client.is_connected:
            await self._record_redis(identifier)
        else:
            self._record_memory(identifier)

    async def _is_limited_redis(self, identifier: str) -> bool:
        key = self._make_key(identifier)
        now = datetime.now(UTC).timestamp()
        cutoff = now - self._window_seconds

        try:
            p = await redis_client.pipeline(transaction=False)
            if p is None:
                return self._is_limited_memory(identifier)
            async with p:
                p.zremrangebyscore(key, "-inf", cutoff)
                p.zcard(key)
                results = await p.execute()

            count = results[1] if results else 0
            return count >= self._max_attempts
        except Exception:
            logger.exception("Redis rate limit check failed, falling back to memory")
            return self._is_limited_memory(identifier)

    async def _record_redis(self, identifier: str) -> None:
        key = self._make_key(identifier)
        now = datetime.now(UTC).timestamp()

        try:
            p = await redis_client.pipeline(transaction=False)
            if p is None:
                self._record_memory(identifier)
                return
            async with p:
                p.zadd(key, {str(now): now})
                p.expire(key, self._window_seconds * 2)
                await p.execute()
        except Exception:
            logger.exception("Redis rate limit record failed")
            self._record_memory(identifier)

    def _is_limited_memory(self, identifier: str) -> bool:
        now = datetime.now(UTC)
        cutoff = now - timedelta(seconds=self._window_seconds)
        attempts = self._in_memory.get(identifier, [])
        self._in_memory[identifier] = [ts for ts in attempts if ts > cutoff]
        return len(self._in_memory[identifier]) >= self._max_attempts

    def _record_memory(self, identifier: str) -> None:
        if identifier not in self._in_memory:
            self._in_memory[identifier] = []
        self._in_memory[identifier].append(datetime.now(UTC))


# Shared instances used across route handlers
register_limiter = SlidingWindowRateLimiter("rl:register", 5, 60)
alignment_limiter = SlidingWindowRateLimiter("rl:alignment", 10, 60)
mfa_limiter = SlidingWindowRateLimiter("rl:mfa", 5, 60)
assessment_limiter = SlidingWindowRateLimiter("rl:assessment", 10, 60)
