from __future__ import annotations

from app.domain.models import get_model_readiness_snapshot


def test_model_readiness_snapshot_includes_operational_metadata() -> None:
    snapshot = get_model_readiness_snapshot()

    assert "ready" in snapshot
    assert "models" in snapshot
    assert "preload_task_status" in snapshot
    assert "realtime_inference_timeout_seconds" in snapshot
    assert all("load_duration_seconds" in model for model in snapshot["models"])
