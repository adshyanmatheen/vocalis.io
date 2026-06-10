from __future__ import annotations

from httpx import AsyncClient

from app.domain.models import get_model_readiness_snapshot


def test_model_readiness_snapshot_includes_operational_metadata() -> None:
    snapshot = get_model_readiness_snapshot()

    assert "ready" in snapshot
    assert "models" in snapshot
    assert "preload_task_status" in snapshot
    assert "realtime_inference_timeout_seconds" in snapshot
    assert all("load_duration_seconds" in model for model in snapshot["models"])


async def test_health_models_endpoint_returns_expected_shape(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get("/api/v1/health/models")

    assert response.status_code == 200
    data = response.json()
    assert "ready" in data
    assert "status" in data
    assert "cache_dir" in data
    assert "device" in data
    assert "started_at" in data
    assert "preload_task_status" in data
    assert "realtime_inference_timeout_seconds" in data
    assert isinstance(data["models"], list)
