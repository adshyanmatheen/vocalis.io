from __future__ import annotations

import asyncio
import base64
from collections import deque
from datetime import UTC, datetime

import numpy as np
import pytest

from app.api.websockets import assessment
from app.api.websockets.assessment import (
    capture_message_metadata,
    handle_audio_chunk,
    handle_end_assessment,
    handle_start_assessment,
)
from app.api.websockets.auth import extract_websocket_token
from app.api.websockets.models import RealtimeAssessmentSession
from app.domain.auth.constants import ACCESS_TOKEN_COOKIE_NAME


class FakeWebSocket:
    def __init__(
        self,
        *,
        query_params: dict[str, str] | None = None,
        headers: dict[str, str] | None = None,
        cookies: dict[str, str] | None = None,
    ) -> None:
        self.query_params = query_params or {}
        self.headers = headers or {}
        self.cookies = cookies or {}


def make_session(*, target_text: str = "") -> RealtimeAssessmentSession:
    now = datetime.now(UTC)

    return RealtimeAssessmentSession(
        user_id=1,
        target_text=target_text,
        sample_rate=16000,
        audio_buffer=deque(),
        buffered_samples=0,
        received_samples=0,
        partial_transcript="",
        last_activity=now,
        started_at=now,
        processed_samples=0,
        last_sequence=None,
        inference_in_progress=False,
        inference_task=None,
        inference_error=None,
        message_metadata=[],
        scoring_windows=[],
    )


def test_websocket_metadata_capture_excludes_audio() -> None:
    session = make_session(target_text="hello")

    capture_message_metadata(
        session=session,
        message={
            "type": "audio_chunk",
            "sequence": 1,
            "sample_rate": 16000,
            "audio": "raw-audio-must-not-be-captured",
        },
        validation_status="valid",
        processing_status="buffered",
    )

    metadata = session.message_metadata[0]

    assert metadata.type == "audio_chunk"
    assert metadata.sequence == 1
    assert not hasattr(metadata, "audio")


def test_websocket_auth_extracts_query_token_before_cookie() -> None:
    websocket = FakeWebSocket(
        query_params={"token": "query-token"},
        cookies={ACCESS_TOKEN_COOKIE_NAME: "cookie-token"},
    )

    assert extract_websocket_token(websocket) == "query-token"


def test_websocket_auth_extracts_cookie_token() -> None:
    websocket = FakeWebSocket(
        cookies={ACCESS_TOKEN_COOKIE_NAME: "cookie-token"},
    )

    assert extract_websocket_token(websocket) == "cookie-token"


def test_websocket_auth_extracts_cookie_header_token() -> None:
    websocket = FakeWebSocket(
        headers={"Cookie": f"{ACCESS_TOKEN_COOKIE_NAME}=header-cookie-token"},
    )

    assert extract_websocket_token(websocket) == "header-cookie-token"


async def test_start_assessment_initializes_session_and_sends_event(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sent_payloads = []

    async def fake_send_json(*, user_id: int, payload):
        sent_payloads.append((user_id, payload))

    monkeypatch.setattr(assessment.connection_manager, "send_json", fake_send_json)
    monkeypatch.setattr(assessment, "models_are_ready", lambda: True)

    session = make_session()

    await handle_start_assessment(
        user_id=1,
        session=session,
        message={
            "type": "start_assessment",
            "target_text": "The quick brown fox",
            "sample_rate": 16000,
        },
    )

    assert session.target_text == "The quick brown fox"
    assert session.sample_rate == 16000
    assert len(session.audio_buffer) == 0
    assert session.buffered_samples == 0
    assert session.received_samples == 0
    assert session.message_metadata[0].processing_status == "started"
    assert sent_payloads[0][0] == 1
    assert sent_payloads[0][1].type == "assessment_started"


async def test_start_assessment_rejects_when_models_are_not_ready(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sent_payloads = []

    async def fake_send_json(*, user_id: int, payload):
        sent_payloads.append((user_id, payload))

    monkeypatch.setattr(assessment.connection_manager, "send_json", fake_send_json)
    monkeypatch.setattr(assessment, "models_are_ready", lambda: False)
    monkeypatch.setattr(
        assessment,
        "model_readiness_error_message",
        lambda: "The assessment engine is not ready.",
    )

    session = make_session()

    await handle_start_assessment(
        user_id=1,
        session=session,
        message={
            "type": "start_assessment",
            "target_text": "The quick brown fox",
            "sample_rate": 16000,
        },
    )

    assert session.target_text == ""
    assert session.message_metadata[0].processing_status == "rejected"
    assert sent_payloads[0][1].type == "assessment_error"
    assert sent_payloads[0][1].message == "The assessment engine is not ready."


async def test_audio_chunk_buffers_pcm16_and_captures_metadata(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    async def fake_maybe_schedule_window(*, user_id: int, session):
        return None

    monkeypatch.setattr(assessment, "maybe_schedule_window", fake_maybe_schedule_window)

    session = make_session(target_text="The quick brown fox")
    waveform = np.array([0, 1000, -1000], dtype=np.int16)
    encoded_audio = base64.b64encode(waveform.tobytes()).decode()

    await handle_audio_chunk(
        user_id=1,
        session=session,
        message={
            "type": "audio_chunk",
            "audio": encoded_audio,
            "sequence": 1,
            "sample_rate": 16000,
        },
    )

    metadata = session.message_metadata[0]

    assert len(session.audio_buffer) == 1
    assert session.buffered_samples == 3
    assert session.received_samples == 3
    assert session.audio_buffer[0].dtype == np.float32
    assert session.last_sequence == 1
    assert metadata.type == "audio_chunk"
    assert metadata.processing_status == "buffered"
    assert not hasattr(metadata, "audio")


async def test_audio_chunk_before_start_sends_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sent_payloads = []

    async def fake_send_json(*, user_id: int, payload):
        sent_payloads.append((user_id, payload))

    monkeypatch.setattr(assessment.connection_manager, "send_json", fake_send_json)

    session = make_session()

    await handle_audio_chunk(
        user_id=1,
        session=session,
        message={
            "type": "audio_chunk",
            "audio": "unused",
            "sequence": 1,
            "sample_rate": 16000,
        },
    )

    metadata = session.message_metadata[0]

    assert metadata.validation_status == "invalid"
    assert metadata.processing_status == "rejected"
    assert sent_payloads[0][1].type == "assessment_error"


async def test_audio_chunk_rejects_out_of_order_sequence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sent_payloads = []

    async def fake_send_json(*, user_id: int, payload):
        sent_payloads.append((user_id, payload))

    monkeypatch.setattr(assessment.connection_manager, "send_json", fake_send_json)

    session = make_session(target_text="The quick brown fox")
    waveform = np.array([0, 1000], dtype=np.int16)
    encoded_audio = base64.b64encode(waveform.tobytes()).decode()

    await handle_audio_chunk(
        user_id=1,
        session=session,
        message={
            "type": "audio_chunk",
            "audio": encoded_audio,
            "sequence": 2,
            "sample_rate": 16000,
        },
    )

    assert len(session.audio_buffer) == 0
    assert sent_payloads[0][1].type == "assessment_error"
    assert "sequence must be 1" in sent_payloads[0][1].message


async def test_end_assessment_sends_clean_error_for_failed_inference_task(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    sent_payloads = []

    async def fake_send_json(*, user_id: int, payload):
        sent_payloads.append((user_id, payload))

    async def failed_inference_task() -> None:
        session.inference_error = "Model inference failed."

    monkeypatch.setattr(assessment.connection_manager, "send_json", fake_send_json)

    session = make_session(target_text="The quick brown fox")
    session.inference_in_progress = True
    session.inference_task = asyncio.create_task(failed_inference_task())
    session.audio_buffer.append(np.array([0.1, 0.2], dtype=np.float32))

    await handle_end_assessment(
        user_id=1,
        session=session,
        message={"type": "end_assessment"},
        database_session=None,
    )

    assert sent_payloads[0][1].type == "assessment_error"
    assert sent_payloads[0][1].message == "Model inference failed."
