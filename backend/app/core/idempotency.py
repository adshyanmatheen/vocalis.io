from __future__ import annotations

import hashlib
import logging

from litestar.connection import Request
from litestar.exceptions import ClientException
from litestar.types import ASGIApp, Receive, Scope, Send

from app.core.redis import redis_client

logger = logging.getLogger(__name__)

IDEMPOTENCY_TTL_SECONDS = 3600
IDEMPOTENCY_HEADER = "Idempotency-Key"


class IdempotencyMiddleware:
    def __init__(self, app: ASGIApp, exclude: str | list[str] | None = None) -> None:
        self.app = app
        self.exclude_prefixes = (
            ["/health", "/ready", "/metrics"] if exclude is None else exclude
        )

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET")
        if method in {"GET", "HEAD", "OPTIONS"}:
            await self.app(scope, receive, send)
            return

        path = scope.get("path", "")
        if any(path.startswith(p) for p in self.exclude_prefixes):
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        idempotency_key = request.headers.get(IDEMPOTENCY_HEADER)

        if idempotency_key is None:
            await self.app(scope, receive, send)
            return

        if not idempotency_key.strip():
            raise ClientException(
                f"{IDEMPOTENCY_HEADER} header cannot be empty.",
                status_code=400,
            )

        key_hash = hashlib.sha256(
            f"{idempotency_key}:{method}:{path}".encode()
        ).hexdigest()
        redis_key = f"idempotency:{key_hash}"

        stored = await redis_client.get(redis_key)
        if stored is not None:
            logger.info("Idempotent request replay detected: %s", idempotency_key)
            raise ClientException(
                "This request has already been processed.",
                status_code=409,
                headers={IDEMPOTENCY_HEADER: idempotency_key},
            )

        await redis_client.setex(redis_key, IDEMPOTENCY_TTL_SECONDS, method)

        await self.app(scope, receive, send)


def create_idempotency_middleware(app: ASGIApp) -> IdempotencyMiddleware:
    return IdempotencyMiddleware(app)
