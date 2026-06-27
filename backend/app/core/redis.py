from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class RedisClient:
    def __init__(self) -> None:
        self._client: Any = None
        self._connected = False

    async def connect(self, url: str | None) -> None:
        if not url:
            logger.info("Redis not configured — running without Redis")
            return
        try:
            import redis.asyncio as aioredis

            self._client = aioredis.from_url(
                url,
                decode_responses=True,
                socket_connect_timeout=3,
                socket_timeout=3,
                retry_on_timeout=True,
                health_check_interval=15,
            )
            await self._client.ping()
            self._connected = True
            logger.info(
                "Connected to Redis at %s", url.split("@")[-1] if "@" in url else url
            )
        except Exception:
            logger.warning("Failed to connect to Redis — running without Redis")
            self._client = None
            self._connected = False

    async def disconnect(self) -> None:
        if self._client is not None:
            try:
                await self._client.aclose()
            except Exception:
                pass
            self._client = None
            self._connected = False

    @property
    def is_connected(self) -> bool:
        return self._connected and self._client is not None

    async def setex(self, key: str, seconds: int, value: str) -> None:
        if self._client is None:
            return
        try:
            await self._client.setex(key, seconds, value)
        except Exception:
            logger.exception("Redis setex failed for key %s", key)

    async def get(self, key: str) -> str | None:
        if self._client is None:
            return None
        try:
            return await self._client.get(key)
        except Exception:
            logger.exception("Redis get failed for key %s")
            return None

    async def delete(self, key: str) -> None:
        if self._client is None:
            return
        try:
            await self._client.delete(key)
        except Exception:
            logger.exception("Redis delete failed for key %s", key)

    async def expire(self, key: str, seconds: int) -> None:
        if self._client is None:
            return
        try:
            await self._client.expire(key, seconds)
        except Exception:
            pass

    async def incr(self, key: str) -> int:
        if self._client is None:
            return 0
        try:
            return await self._client.incr(key)
        except Exception:
            logger.exception("Redis incr failed for key %s", key)
            return 0

    async def zadd(self, key: str, mapping: dict[str | bytes, float]) -> int:
        if self._client is None:
            return 0
        try:
            return await self._client.zadd(key, mapping)
        except Exception:
            logger.exception("Redis zadd failed for key %s", key)
            return 0

    async def zremrangebyscore(
        self, key: str, min: float | str, max: float | str
    ) -> int:
        if self._client is None:
            return 0
        try:
            return await self._client.zremrangebyscore(key, min, max)
        except Exception:
            logger.exception("Redis zremrangebyscore failed for key %s", key)
            return 0

    async def zcard(self, key: str) -> int:
        if self._client is None:
            return 0
        try:
            return await self._client.zcard(key)
        except Exception:
            logger.exception("Redis zcard failed for key %s", key)
            return 0

    async def pipeline(self, transaction: bool = True) -> Any | None:
        if self._client is None:
            return None
        try:
            return await self._client.pipeline(transaction=transaction)
        except Exception:
            return None


redis_client = RedisClient()
