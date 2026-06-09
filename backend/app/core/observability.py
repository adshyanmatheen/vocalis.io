from __future__ import annotations

import logging
import time
import uuid

from litestar.types import ASGIApp, Message, Receive, Scope, Send

logger = logging.getLogger("vocalis.request")

REQUEST_ID_HEADER = b"x-request-id"


class RequestObservabilityMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in {"http", "websocket"}:
            await self.app(scope, receive, send)
            return

        request_id = self._get_request_id(scope)
        scope.setdefault("state", {})["request_id"] = request_id
        started = time.perf_counter()
        status_code: int | None = None

        async def send_wrapper(message: Message) -> None:
            nonlocal status_code
            if message["type"] == "http.response.start":
                status_code = int(message["status"])
                headers = list(message.get("headers", []))
                headers.append((REQUEST_ID_HEADER, request_id.encode("ascii")))
                message["headers"] = headers

            await send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.info(
                "request_id=%s type=%s method=%s path=%s status=%s duration_ms=%.2f",
                request_id,
                scope["type"],
                scope.get("method", "WEBSOCKET"),
                scope.get("path", ""),
                status_code if status_code is not None else "-",
                duration_ms,
            )

    def _get_request_id(self, scope: Scope) -> str:
        headers: list[tuple[bytes, bytes]] = list(scope.get("headers") or [])
        for key, value in headers:
            if key.lower() == REQUEST_ID_HEADER:
                decoded = value.decode("ascii", errors="ignore").strip()
                if decoded:
                    return decoded[:128]

        return uuid.uuid4().hex


def create_request_observability_middleware(
    app: ASGIApp,
) -> RequestObservabilityMiddleware:
    return RequestObservabilityMiddleware(app)
