from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str


class ModelHealthItemResponse(BaseModel):
    name: str
    model_id: str
    status: str
    error: str | None
    updated_at: str | None
    load_started_at: str | None = None
    load_finished_at: str | None = None
    load_duration_seconds: float | None = None


class ModelHealthResponse(BaseModel):
    ready: bool
    status: str
    cache_dir: str
    device: str
    started_at: str
    preload_task_status: str
    realtime_inference_timeout_seconds: float
    models: list[ModelHealthItemResponse]
