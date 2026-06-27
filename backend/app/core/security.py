from __future__ import annotations

import secrets

from litestar.types import ASGIApp, Message, Receive, Scope, Send

CSP_DEFAULT_SRC = [
    "'self'",
    "https://fonts.googleapis.com",
    "https://fonts.gstatic.com",
    "https://ka-f.fontawesome.com",
]
CSP_SCRIPT_SRC = ["'self'"]
CSP_STYLE_SRC = [
    "'self'",
    "'unsafe-inline'",
    "https://fonts.googleapis.com",
]
CSP_IMG_SRC = ["'self'", "data:", "blob:"]
CSP_CONNECT_SRC = ["'self'", "ws:", "wss:"]
CSP_FONT_SRC = ["'self'", "https://fonts.gstatic.com", "https://ka-f.fontawesome.com"]
CSP_FRAME_ANCESTORS = ["'none'"]
CSP_FORM_ACTION = ["'self'"]


def _build_csp(nonce: str) -> str:
    directives = [
        f"default-src {' '.join(CSP_DEFAULT_SRC)}",
        f"script-src {' '.join(CSP_SCRIPT_SRC)} 'nonce-{nonce}' 'strict-dynamic'",
        f"style-src {' '.join(CSP_STYLE_SRC)}",
        f"img-src {' '.join(CSP_IMG_SRC)}",
        f"connect-src {' '.join(CSP_CONNECT_SRC)}",
        f"font-src {' '.join(CSP_FONT_SRC)}",
        "frame-ancestors " + " ".join(CSP_FRAME_ANCESTORS),
        f"form-action {' '.join(CSP_FORM_ACTION)}",
        "base-uri 'self'",
    ]
    return "; ".join(directives)


class SecurityHeadersMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        nonce = secrets.token_hex(16)
        csp = _build_csp(nonce)

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
                        b"geolocation=(), microphone=self, camera=()",
                    ),
                    (b"content-security-policy", csp.encode("ascii")),
                ]
                for header_name, header_value in security_headers:
                    if not any(h[0].lower() == header_name for h in headers):
                        headers.append((header_name, header_value))
                message["headers"] = headers

            await send(message)

        await self.app(scope, receive, send_wrapper)


def create_security_headers_middleware(app: ASGIApp) -> SecurityHeadersMiddleware:
    return SecurityHeadersMiddleware(app)
