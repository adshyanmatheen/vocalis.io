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
from app.core.config import (
    settings,
)
from app.core.logging import configure_logging
from app.core.observability import create_request_observability_middleware
from app.core.security import create_security_headers_middleware
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
        allow_headers=["Content-Type", "Authorization"],
    ),
    dependencies={
        "database_session": (Provide(provide_database_session)),
        "current_user": (Provide(provide_current_user)),
        "authenticated_user": (require_authenticated_user_provide),
    },
    middleware=[
        DefineMiddleware(create_security_headers_middleware),
        DefineMiddleware(create_request_observability_middleware),
    ],
    on_startup=[
        initialize_database,
        start_local_model_preload,
    ],
    on_shutdown=[
        create_database_backup_async,
        dispose_database_engine,
    ],
)
