from __future__ import annotations

import logging
import secrets
from urllib.parse import urlparse

from litestar.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings

logger = logging.getLogger(__name__)

CSRF_COOKIE_NAME = "csrf_token"
SAFE_METHODS = frozenset({"GET", "HEAD", "OPTIONS", "TRACE"})


def _origin_allowed(origin: str) -> bool:
    parsed = urlparse(origin)
    hostname = parsed.hostname or ""
    for allowed in settings.app.cors_allowed_origins:
        allowed_hostname = urlparse(allowed).hostname or allowed
        if hostname == allowed_hostname:
            return True
    if settings.app.environment == "development" and hostname in {
        "localhost",
        "127.0.0.1",
    }:
        return True
    return False


def _build_cookie(value: str) -> str:
    secure = settings.app.environment == "production"
    parts = [
        f"{CSRF_COOKIE_NAME}={value}",
        "Path=/",
        "SameSite=Strict",
    ]
    if secure:
        parts.append("Secure")
    return "; ".join(parts)


def _parse_cookies(cookie_string: str) -> dict[str, str]:
    cookies: dict[str, str] = {}
    for part in cookie_string.split(";"):
        part = part.strip()
        if "=" in part:
            key, value = part.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


class CSRFProtectionMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or settings.app.environment == "testing":
            await self.app(scope, receive, send)
            return

        method = scope.get("method", "GET")
        headers_list: list[tuple[bytes, bytes]] = list(scope.get("headers") or [])
        headers = {k.decode(): v.decode() for k, v in headers_list if k is not None}

        raw_cookie = headers.get("cookie", "")
        cookies = _parse_cookies(raw_cookie)
        csrf_cookie = cookies.get(CSRF_COOKIE_NAME, "")

        if method not in SAFE_METHODS and csrf_cookie:
            origin = headers.get("origin", "")
            if origin and not _origin_allowed(origin):
                logger.warning(
                    "CSRF: origin %s not allowed for %s %s",
                    origin,
                    method,
                    scope.get("path"),
                )
                await self._reject(send)
                return

            csrf_header = headers.get("x-csrf-token", "")
            if not csrf_header or csrf_header != csrf_cookie:
                logger.warning(
                    "CSRF: token mismatch for %s %s (header=%s cookie=%s)",
                    method,
                    scope.get("path"),
                    csrf_header,
                    csrf_cookie,
                )
                await self._reject(send)
                return

        token = csrf_cookie or secrets.token_urlsafe(32)

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                msg_headers = list(message.get("headers", []))
                names = {h[0].lower() for h in msg_headers}
                if b"set-cookie" not in names:
                    msg_headers.append((b"set-cookie", _build_cookie(token).encode()))
                message["headers"] = msg_headers
            await send(message)

        await self.app(scope, receive, send_wrapper)

    async def _reject(self, send: Send) -> None:
        body = b'{"detail":"CSRF validation failed"}'
        await send(
            {
                "type": "http.response.start",
                "status": 403,
                "headers": [
                    (b"content-type", b"application/json"),
                    (b"content-length", str(len(body)).encode()),
                ],
            }
        )
        await send(
            {
                "type": "http.response.body",
                "body": body,
            }
        )


def create_csrf_middleware(app: ASGIApp) -> CSRFProtectionMiddleware:
    return CSRFProtectionMiddleware(app)
