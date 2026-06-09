from __future__ import annotations

from collections import deque
from datetime import UTC, datetime

import numpy as np
import pytest

from app.api.websockets.models import RealtimeAssessmentSession
from app.domain.alignment.engine import load_alignment_model_bundle
from app.domain.phoneme.engine import load_phoneme_model_bundle
from app.domain.realtime import tasks
from app.domain.realtime.service import (
    RealtimeAssessmentService,
    realtime_assessment_service,
)


def test_realtime_partial_feedback_shape() -> None:
    service = RealtimeAssessmentService()
    scoring_payload = {
        "overall_score": 0.72,
        "performance_band": "On Track",
        "word_scores": [
            {
                "word": "quick",
                "score": 0.82,
            }
        ],
        "phoneme_results": [
            {
                "expected_phoneme": "k",
                "phoneme_score": 0.91,
            },
            {
                "expected_phoneme": "r",
                "phoneme_score": 0.42,
            },
        ],
    }

    feedback = service.build_partial_feedback(scoring_payload=scoring_payload)

    assert feedback["overall_score"] == 0.72
    assert feedback["weak_phonemes"] == ["r"]
    assert feedback["performance_band"] == "On Track"
    assert feedback["word_scores"][0]["word"] == "quick"


def test_realtime_aggregate_scoring_windows() -> None:
    service = RealtimeAssessmentService()

    aggregate = service.aggregate_scoring_windows(
        scoring_windows=[
            {
                "overall_score": 0.8,
                "word_scores": [{"word": "hello", "score": 0.8}],
                "phoneme_results": [{"expected_phoneme": "h", "phoneme_score": 0.8}],
            },
            {
                "overall_score": 0.6,
                "word_scores": [{"word": "world", "score": 0.6}],
                "phoneme_results": [{"expected_phoneme": "w", "phoneme_score": 0.5}],
            },
        ],
    )

    assert aggregate["overall_score"] == 0.7
    assert aggregate["performance_band"] == "On Track"
    assert len(aggregate["word_scores"]) == 2
    assert len(aggregate["phoneme_results"]) == 2


async def test_realtime_inference_sends_partial_feedback(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sent_payloads = []

    def fake_process_audio_window(*, waveform, target_text: str, sample_rate: int):
        return {
            "overall_score": 0.81,
            "performance_band": "Strong",
            "word_scores": [{"word": target_text, "score": 0.81}],
            "phoneme_results": [
                {
                    "expected_phoneme": "r",
                    "phoneme_score": 0.5,
                }
            ],
        }

    async def fake_send_json(*, user_id: int, payload):
        sent_payloads.append((user_id, payload))

    async def fake_on_complete() -> None:
        return None

    monkeypatch.setattr(
        realtime_assessment_service,
        "process_audio_window",
        fake_process_audio_window,
    )
    monkeypatch.setattr(tasks.connection_manager, "send_json", fake_send_json)

    now = datetime.now(UTC)
    session = RealtimeAssessmentSession(
        user_id=1,
        target_text="hello",
        sample_rate=16000,
        audio_buffer=deque(),
        buffered_samples=0,
        received_samples=0,
        partial_transcript="",
        last_activity=now,
        started_at=now,
        processed_samples=0,
        last_sequence=None,
        inference_in_progress=True,
        inference_task=None,
        inference_error=None,
        message_metadata=[],
        scoring_windows=[],
    )

    await tasks.run_realtime_inference(
        user_id=1,
        session=session,
        waveform=np.array([0.0, 0.1], dtype=np.float32),
        on_complete=fake_on_complete,
    )

    assert session.inference_in_progress is False
    assert session.inference_task is None
    assert session.scoring_windows[0]["overall_score"] == 0.81
    assert sent_payloads[0][0] == 1
    assert sent_payloads[0][1].type == "partial_feedback"
    assert sent_payloads[0][1].weak_phonemes == ["r"]


@pytest.mark.model
def test_model_bundles_load() -> None:
    alignment_bundle = load_alignment_model_bundle()
    phoneme_bundle = load_phoneme_model_bundle()

    assert alignment_bundle.model is not None
    assert alignment_bundle.processor is not None
    assert phoneme_bundle.model is not None
    assert phoneme_bundle.processor is not None


@pytest.mark.model
def test_model_backed_realtime_assessment_smoke(
    synthetic_waveform,
    synthetic_target_text: str,
) -> None:
    service = RealtimeAssessmentService()

    scoring_payload = service.process_audio_window(
        waveform=synthetic_waveform,
        target_text=synthetic_target_text,
        sample_rate=16000,
    )

    assert "overall_score" in scoring_payload
    assert "performance_band" in scoring_payload
    assert "phoneme_results" in scoring_payload
