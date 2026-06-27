import asyncio
import logging

from litestar import (
    Litestar,
)
from litestar.config.cors import CORSConfig
from litestar.di import (
    Provide,
)
from litestar.middleware import DefineMiddleware

from app.api.router import (
    routes,
)
from app.api.websockets.assessment import (
    assessment_websocket_handler,
)
from app.api.websockets.manager import connection_manager
from app.core.config import (
    settings,
)
from app.core.csrf import create_csrf_middleware
from app.core.idempotency import create_idempotency_middleware
from app.core.logging import configure_logging
from app.core.metrics import create_metrics_middleware, metrics_endpoint
from app.core.observability import create_request_observability_middleware
from app.core.rate_limit_middleware import RateLimitHeadersMiddleware
from app.core.redis import redis_client
from app.core.security import create_security_headers_middleware
from app.core.sentry import create_sentry_middleware, init_sentry
from app.domain.auth.dependencies import (
    provide_current_user,
)
from app.domain.auth.guards import (
    require_authenticated_user_provide,
)
from app.domain.database.backup import (
    create_database_backup_async,
)
from app.domain.database.dependencies import (
    provide_database_session,
)
from app.domain.database.init import (
    initialize_database,
)
from app.domain.database.shutdown import (
    dispose_database_engine,
)
from app.domain.models import (
    start_local_model_preload,
)

logger = logging.getLogger(__name__)

configure_logging()
init_sentry()


async def _startup() -> None:
    pruning_task = asyncio.create_task(connection_manager.run_pruning_loop())

    def _on_pruning_done(task: asyncio.Task[None]) -> None:
        if not task.cancelled() and task.exception() is not None:
            logger.error(
                "Pruning loop exited with exception", exc_info=task.exception()
            )

    pruning_task.add_done_callback(_on_pruning_done)

    await asyncio.gather(
        initialize_database(),
        start_local_model_preload(),
        redis_client.connect(settings.app.redis_url),
    )


async def _on_shutdown_backup() -> None:
    try:
        await asyncio.wait_for(create_database_backup_async(), timeout=30)
    except Exception:
        logger.exception("Backup on shutdown failed")


async def _on_shutdown_database() -> None:
    try:
        await asyncio.wait_for(dispose_database_engine(), timeout=10)
    except Exception:
        logger.exception("Database dispose on shutdown failed")


async def _on_shutdown_redis() -> None:
    try:
        await asyncio.wait_for(redis_client.disconnect(), timeout=5)
    except Exception:
        logger.exception("Redis disconnect on shutdown failed")


app = Litestar(
    route_handlers=(
        [
            *routes,
            assessment_websocket_handler,
            metrics_endpoint,
        ]
    ),
    debug=settings.app.debug,
    cors_config=CORSConfig(
        allow_origins=settings.app.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["Content-Type", "Authorization", "X-CSRF-Token"],
    ),
    dependencies={
        "database_session": (Provide(provide_database_session)),
        "current_user": (Provide(provide_current_user)),
        "authenticated_user": (require_authenticated_user_provide),
    },
    middleware=[
        DefineMiddleware(create_csrf_middleware),
        DefineMiddleware(create_sentry_middleware),
        DefineMiddleware(create_security_headers_middleware),
        DefineMiddleware(create_request_observability_middleware),
        DefineMiddleware(create_metrics_middleware),
        DefineMiddleware(create_idempotency_middleware),
        DefineMiddleware(RateLimitHeadersMiddleware),
    ],
    on_startup=[
        _startup,
    ],
    on_shutdown=[
        _on_shutdown_backup,
        _on_shutdown_database,
        _on_shutdown_redis,
    ],
)
