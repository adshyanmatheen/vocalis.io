import asyncio

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
from app.core.logging import configure_logging
from app.core.observability import create_request_observability_middleware
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

configure_logging()
init_sentry()


async def _startup() -> None:
    asyncio.create_task(connection_manager.run_pruning_loop())

    await asyncio.gather(
        initialize_database(),
        start_local_model_preload(),
    )


app = Litestar(
    route_handlers=(
        [
            *routes,
            assessment_websocket_handler,
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
    ],
    on_startup=[
        _startup,
    ],
    on_shutdown=[
        lambda: asyncio.wait_for(create_database_backup_async(), timeout=30),
        lambda: asyncio.wait_for(dispose_database_engine(), timeout=10),
    ],
)
