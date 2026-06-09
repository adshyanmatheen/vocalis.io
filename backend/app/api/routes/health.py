from litestar import get

from app.core.config import (
    settings,
)
from app.domain.models import get_model_readiness_snapshot
from app.schemas.responses.health import (
    HealthResponse,
    ModelHealthResponse,
)


@get(
    path="/health",
    sync_to_thread=False,
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="online",
        service=settings.app.app_name,
    )


@get(
    path="/health/models",
    sync_to_thread=False,
)
def model_health_check() -> ModelHealthResponse:
    return ModelHealthResponse.model_validate(get_model_readiness_snapshot())
