from __future__ import annotations

from litestar.connection import Request
from litestar.middleware import AbstractMiddleware
from litestar.types import ASGIApp, Receive, Scope, Send


class RateLimitHeadersMiddleware(AbstractMiddleware):
    def __init__(self, app: ASGIApp, exclude: str | list[str] | None = None) -> None:
        super().__init__(app, exclude=exclude)

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        rate_limit = getattr(request.state, "rate_limit", None)

        if rate_limit is None:
            await self.app(scope, receive, send)
            return

        async def send_with_headers(message: dict) -> None:
            if message["type"] == "http.response.start":
                headers = message.get("headers", [])
                headers.extend(
                    [
                        (b"X-RateLimit-Limit", str(rate_limit.limit).encode()),
                        (b"X-RateLimit-Remaining", str(rate_limit.remaining).encode()),
                        (b"X-RateLimit-Reset", str(rate_limit.reset_at).encode()),
                    ]
                )
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_with_headers)
