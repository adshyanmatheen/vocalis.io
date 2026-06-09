from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from threading import RLock
from time import perf_counter
from typing import Literal

from app.core.config import settings
from app.domain.alignment.engine import load_alignment_model_bundle
from app.domain.phoneme.constants import PHONEME_MODEL_NAME
from app.domain.phoneme.engine import load_phoneme_model_bundle

logger = logging.getLogger(__name__)

ModelReadinessState = Literal["not_loaded", "loading", "ready", "failed"]


@dataclass
class ModelReadiness:
    name: str
    model_id: str
    status: ModelReadinessState = "not_loaded"
    error: str | None = None
    updated_at: str | None = None
    load_started_at: str | None = None
    load_finished_at: str | None = None
    load_duration_seconds: float | None = None


_readiness_lock = RLock()
_preload_task: asyncio.Task[None] | None = None
_service_started_at = datetime.now(UTC).isoformat()
_model_readiness: dict[str, ModelReadiness] = {
    "alignment": ModelReadiness(
        name="alignment",
        model_id=settings.app.huggingface_model_id,
    ),
    "phoneme": ModelReadiness(
        name="phoneme",
        model_id=PHONEME_MODEL_NAME,
    ),
}


def _timestamp() -> str:
    return datetime.now(UTC).isoformat()


def _set_status(
    *,
    model_name: str,
    status: ModelReadinessState,
    error: str | None = None,
) -> None:
    with _readiness_lock:
        model = _model_readiness[model_name]
        model.status = status
        model.error = error
        model.updated_at = _timestamp()
        if status == "loading":
            model.load_started_at = model.updated_at
            model.load_finished_at = None
            model.load_duration_seconds = None
        if status in {"ready", "failed"}:
            model.load_finished_at = model.updated_at


def _load_model(
    *,
    model_name: str,
    loader,
    local_files_only: bool,
) -> None:
    started = perf_counter()
    _set_status(model_name=model_name, status="loading")

    try:
        loader(local_files_only=local_files_only)

    except Exception as error:
        logger.exception("Model %s failed to load", model_name)
        _set_status(model_name=model_name, status="failed", error=str(error))
        with _readiness_lock:
            _model_readiness[model_name].load_duration_seconds = round(
                perf_counter() - started, 4
            )
        raise

    _set_status(model_name=model_name, status="ready")
    with _readiness_lock:
        _model_readiness[model_name].load_duration_seconds = round(
            perf_counter() - started, 4
        )


def warm_model_bundles(*, download: bool = False) -> None:
    local_files_only = not download

    import threading

    threads = []
    for model_name, loader in [
        ("alignment", load_alignment_model_bundle),
        ("phoneme", load_phoneme_model_bundle),
    ]:
        t = threading.Thread(
            target=_load_model,
            kwargs=dict(
                model_name=model_name,
                loader=loader,
                local_files_only=local_files_only,
            ),
        )
        t.start()
        threads.append(t)

    for t in threads:
        t.join()


async def _preload_local_models() -> None:
    try:
        await asyncio.to_thread(warm_model_bundles, download=False)

    except Exception:
        logger.exception("Local model preload failed")
        return


async def start_local_model_preload() -> None:
    global _preload_task

    if settings.app.environment == "testing":
        return

    if _preload_task is not None and not _preload_task.done():
        return

    _preload_task = asyncio.create_task(_preload_local_models())


def get_model_readiness_snapshot() -> dict:
    with _readiness_lock:
        models = [
            {
                "name": model.name,
                "model_id": model.model_id,
                "status": model.status,
                "error": model.error,
                "updated_at": model.updated_at,
                "load_started_at": model.load_started_at,
                "load_finished_at": model.load_finished_at,
                "load_duration_seconds": model.load_duration_seconds,
            }
            for model in _model_readiness.values()
        ]
        preload_task_status = (
            "not_started"
            if _preload_task is None
            else "running"
            if not _preload_task.done()
            else "finished"
        )

    return {
        "ready": all(model["status"] == "ready" for model in models),
        "status": "ready"
        if all(model["status"] == "ready" for model in models)
        else "not_ready",
        "cache_dir": settings.app.huggingface_cache_dir,
        "device": settings.app.device,
        "started_at": _service_started_at,
        "preload_task_status": preload_task_status,
        "realtime_inference_timeout_seconds": settings.app.realtime_inference_timeout_seconds,
        "models": models,
    }


def models_are_ready() -> bool:
    return bool(get_model_readiness_snapshot()["ready"])


def model_readiness_error_message() -> str:
    snapshot = get_model_readiness_snapshot()
    loading_models = [
        model["name"] for model in snapshot["models"] if model["status"] == "loading"
    ]
    failed_models = [
        model["name"] for model in snapshot["models"] if model["status"] == "failed"
    ]

    if loading_models:
        return "The assessment engine is still loading. Please try again in a moment."

    if failed_models:
        return "The assessment engine setup is incomplete. Please try again later."

    return "The assessment engine is not ready yet. Please try again later."
