from litestar import get
from litestar.response import Response
from litestar.status_codes import HTTP_200_OK, HTTP_503_SERVICE_UNAVAILABLE

from app.core.config import (
    settings,
)
from app.core.redis import redis_client
from app.domain.database.session import database_engine
from app.domain.models import get_model_readiness_snapshot, models_are_ready
from app.schemas.responses.health import (
    HealthResponse,
    ModelHealthResponse,
    ReadyCheckDetail,
    ReadyResponse,
)


@get(
    path="/health",
    operation_id="healthCheck",
    summary="Service Health Check",
    description="This Route Returns The Current Operational Status Of The Vocalis Service, Including The Application Name And A Health Indicator To Confirm The Backend Is Responsive.",
    tags=["Health"],
    sync_to_thread=False,
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
    sync_to_thread=False,
)
def model_health_check() -> ModelHealthResponse:
    return ModelHealthResponse(**get_model_readiness_snapshot())


@get(
    path="/ready",
    operation_id="readyCheck",
    summary="Readiness Probe",
    description="This Route Checks All Dependencies (Database, Redis, ML Models) And Returns 200 Only When The Service Is Fully Ready To Handle Requests. Returns 503 If Any Dependency Is Unhealthy.",
    tags=["Health"],
)
async def ready_check() -> Response[ReadyResponse]:
    db_ok = False
    db_error: str | None = None
    try:
        async with database_engine.connect() as conn:
            from sqlalchemy import text as sa_text
            await conn.execute(sa_text("SELECT 1"))
            db_ok = True
    except Exception as exc:
        db_error = str(exc)

    redis_ok = await redis_client.ping()

    models_ok = models_are_ready()
    models_error: str | None = None if models_ok else "Models are not fully loaded"

    all_ok = db_ok and redis_ok and models_ok

    return Response(
        content=ReadyResponse(
            ready=all_ok,
            database=ReadyCheckDetail(
                status="healthy" if db_ok else "unhealthy", error=db_error
            ),
            redis=ReadyCheckDetail(
                status="healthy" if redis_ok else "unhealthy",
                error=None if redis_ok else "Redis ping failed",
            ),
            models=ReadyCheckDetail(
                status="healthy" if models_ok else "unhealthy", error=models_error
            ),
        ),
        status_code=HTTP_200_OK if all_ok else HTTP_503_SERVICE_UNAVAILABLE,
    )
