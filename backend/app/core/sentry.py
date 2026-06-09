from __future__ import annotations

import logging

from litestar.types import ASGIApp, Receive, Scope, Send

from app.core.config import settings

logger = logging.getLogger(__name__)


def init_sentry() -> None:
    dsn = settings.app.sentry_dsn
    if not dsn:
        logger.info("Sentry DSN not configured — skipping Sentry initialization")
        return

    import sentry_sdk
    from sentry_sdk.integrations.logging import LoggingIntegration

    sentry_sdk.init(
        dsn=dsn,
        environment=settings.app.environment,
        traces_sample_rate=0.25,
        profiles_sample_rate=0.25,
        send_default_pii=False,
        integrations=[
            LoggingIntegration(level=logging.WARNING, event_level=logging.ERROR),
        ],
    )
    logger.info("Sentry initialized (DSN configured)")


class SentryASGIMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self._enabled = settings.app.sentry_dsn is not None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if not self._enabled or scope["type"] not in {"http", "websocket"}:
            await self.app(scope, receive, send)
            return

        import sentry_sdk

        with sentry_sdk.isolation_scope() as scope_ctx:
            request_id = scope.get("state", {}).get("request_id", "")
            if request_id:
                scope_ctx.set_tag("request_id", request_id)
            scope_ctx.set_tag("method", scope.get("method", ""))
            scope_ctx.set_tag("path", scope.get("path", ""))

            try:
                await self.app(scope, receive, send)
            except Exception:
                sentry_sdk.capture_exception()
                raise


def create_sentry_middleware(app: ASGIApp) -> SentryASGIMiddleware:
    return SentryASGIMiddleware(app)
