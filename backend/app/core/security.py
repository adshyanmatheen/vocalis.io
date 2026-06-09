from __future__ import annotations

from litestar.types import ASGIApp, Message, Receive, Scope, Send


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                security_headers = [
                    (b"x-content-type-options", b"nosniff"),
                    (b"x-frame-options", b"DENY"),
                    (b"x-xss-protection", b"1; mode=block"),
                    (
                        b"strict-transport-security",
                        b"max-age=31536000; includeSubDomains",
                    ),
                    (b"referrer-policy", b"strict-origin-when-cross-origin"),
                    (
                        b"permissions-policy",
                        b"geolocation=(), microphone=(), camera=()",
                    ),
                ]
                for header_name, header_value in security_headers:
                    if not any(h[0].lower() == header_name for h in headers):
                        headers.append((header_name, header_value))
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_wrapper)


def create_security_headers_middleware(app: ASGIApp) -> SecurityHeadersMiddleware:
    return SecurityHeadersMiddleware(app)
