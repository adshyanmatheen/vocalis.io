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
    operation_id="healthCheck",
    summary="Service Health Check",
    description="This Route Returns The Current Operational Status Of The Vocalis Service, Including The Application Name And A Health Indicator To Confirm The Backend Is Responsive.",
    tags=["Health"],
)
def health_check() -> HealthResponse:
    return HealthResponse(
        status="online",
        service=settings.app.app_name,
    )


@get(
    path="/health/models",
    operation_id="modelHealthCheck",
    summary="Model Readiness Check",
    description="This Route Queries All Registered Machine Learning Models And Returns A Readiness Snapshot Indicating Whether Each Model Is Loaded, Cached, And Ready For Inference Tasks.",
    tags=["Health"],
)
def model_health_check() -> ModelHealthResponse:
    return ModelHealthResponse(**get_model_readiness_snapshot())
