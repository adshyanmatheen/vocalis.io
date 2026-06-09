from litestar import (
    Router,
)

from app.api.routes.account import (
    get_account_summary,
)
from app.api.routes.alignment import (
    perform_alignment,
)
from app.api.routes.assessment import get_assessment_history
from app.api.routes.auth import (
    get_current_user,
    login_user,
    logout_user,
    refresh_user_session,
    register_user,
)
from app.api.routes.health import (
    health_check,
    model_health_check,
)
from app.api.routes.mfa import (
    disable_mfa,
    login_with_mfa,
    setup_mfa,
    verify_mfa,
)
from app.api.routes.root import (
    root,
)
from app.api.routes.target import (
    get_current_target,
)

v1_router = Router(
    path="/api/v1",
    route_handlers=[
        root,
        health_check,
        model_health_check,
        register_user,
        login_user,
        refresh_user_session,
        logout_user,
        get_current_user,
        setup_mfa,
        verify_mfa,
        login_with_mfa,
        disable_mfa,
        perform_alignment,
        get_assessment_history,
        get_account_summary,
        get_current_target,
    ],
)


routes = [
    v1_router,
]
