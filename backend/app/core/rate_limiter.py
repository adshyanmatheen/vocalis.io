from __future__ import annotations

import logging
import math
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.core.redis import redis_client

logger = logging.getLogger(__name__)


@dataclass
class RateLimitInfo:
    limit: int
    remaining: int
    reset_at: int


class SlidingWindowRateLimiter:
    def __init__(self, prefix: str, max_attempts: int, window_seconds: int) -> None:
        self._prefix = prefix
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._in_memory: dict[str, list[tuple[datetime, int]]] = {}

    def _make_key(self, identifier: str) -> str:
        return f"{self._prefix}:{identifier}"

    async def is_limited(self, identifier: str) -> bool:
        if redis_client.is_connected:
            return await self._is_limited_redis(identifier)
        return self._is_limited_memory(identifier)

    async def check(self, identifier: str) -> RateLimitInfo:
        if redis_client.is_connected:
            return await self._check_redis(identifier)
        return self._check_memory(identifier)

    async def record(self, identifier: str) -> None:
        if redis_client.is_connected:
            await self._record_redis(identifier)
        else:
            self._record_memory(identifier)

    async def _is_limited_redis(self, identifier: str) -> bool:
        info = await self._check_redis(identifier)
        return info.remaining <= 0

    async def _check_redis(self, identifier: str) -> RateLimitInfo:
        key = self._make_key(identifier)
        now = datetime.now(UTC).timestamp()
        cutoff = now - self._window_seconds

        try:
            p = await redis_client.pipeline(transaction=False)
            if p is None:
                return self._check_memory(identifier)
            async with p:
                p.zremrangebyscore(key, "-inf", cutoff)
                p.zcard(key)
                results = await p.execute()

            count = results[1] if results else 0
            remaining = max(0, self._max_attempts - count)
            reset_at = math.ceil(now + self._window_seconds)
            return RateLimitInfo(
                limit=self._max_attempts, remaining=remaining, reset_at=reset_at
            )
        except Exception:
            logger.exception("Redis rate limit check failed, falling back to memory")
            return self._check_memory(identifier)

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
        return self._check_memory(identifier).remaining <= 0

    def _check_memory(self, identifier: str) -> RateLimitInfo:
        now = datetime.now(UTC)
        now_ts = now.timestamp()
        cutoff = now - timedelta(seconds=self._window_seconds)
        attempts = self._in_memory.get(identifier, [])
        recent = [(ts, r) for ts, r in attempts if ts > cutoff]
        self._in_memory[identifier] = recent
        remaining = max(0, self._max_attempts - len(recent))
        reset_at = math.ceil(now_ts + self._window_seconds)
        return RateLimitInfo(
            limit=self._max_attempts, remaining=remaining, reset_at=reset_at
        )

    def _record_memory(self, identifier: str) -> None:
        if identifier not in self._in_memory:
            self._in_memory[identifier] = []
        self._in_memory[identifier].append((datetime.now(UTC), self._window_seconds))


# Shared instances used across route handlers
register_limiter = SlidingWindowRateLimiter("rl:register", 5, 60)
alignment_limiter = SlidingWindowRateLimiter("rl:alignment", 10, 60)
mfa_limiter = SlidingWindowRateLimiter("rl:mfa", 5, 60)
assessment_limiter = SlidingWindowRateLimiter("rl:assessment", 10, 60)
