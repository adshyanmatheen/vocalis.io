from __future__ import annotations

import pytest
from httpx import AsyncClient

from app.api.routes import health


async def test_health_check(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "online"


async def test_model_health_check(
    async_client: AsyncClient,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        health,
        "get_model_readiness_snapshot",
        lambda: {
            "ready": False,
            "status": "not_ready",
            "cache_dir": ".cache/huggingface",
            "device": "cpu",
            "started_at": "2026-06-02T00:00:00+00:00",
            "preload_task_status": "finished",
            "realtime_inference_timeout_seconds": 60.0,
            "models": [
                {
                    "name": "alignment",
                    "model_id": "alignment-model",
                    "status": "failed",
                    "error": "missing cache",
                    "updated_at": "2026-06-02T00:00:00+00:00",
                    "load_started_at": "2026-06-02T00:00:00+00:00",
                    "load_finished_at": "2026-06-02T00:00:01+00:00",
                    "load_duration_seconds": 1.0,
                },
                {
                    "name": "phoneme",
                    "model_id": "phoneme-model",
                    "status": "ready",
                    "error": None,
                    "updated_at": "2026-06-02T00:00:01+00:00",
                    "load_started_at": "2026-06-02T00:00:00+00:00",
                    "load_finished_at": "2026-06-02T00:00:01+00:00",
                    "load_duration_seconds": 1.0,
                },
            ],
        },
    )

    response = await async_client.get("/api/v1/health/models")

    assert response.status_code == 200
    assert response.json()["ready"] is False
    assert response.json()["preload_task_status"] == "finished"
    assert response.json()["models"][0]["status"] == "failed"
