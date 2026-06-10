from msgspec import Struct


class HealthResponse(Struct, kw_only=True):
    status: str
    service: str


class ModelHealthItemResponse(Struct, kw_only=True):
    name: str
    model_id: str
    status: str
    error: str | None
    updated_at: str | None
    load_started_at: str | None = None
    load_finished_at: str | None = None
    load_duration_seconds: float | None = None


class ModelHealthResponse(Struct, kw_only=True):
    ready: bool
    status: str
    cache_dir: str
    device: str
    started_at: str
    preload_task_status: str
    realtime_inference_timeout_seconds: float
    models: list[ModelHealthItemResponse]
