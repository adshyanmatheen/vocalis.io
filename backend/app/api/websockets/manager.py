from __future__ import annotations

import asyncio
import logging
from collections import deque
from datetime import UTC, datetime
from typing import Any

import msgspec
from litestar import WebSocket

from app.api.websockets.models import (
    RealtimeAssessmentSession,
)
from app.domain.utils import normalize_datetime

logger = logging.getLogger(__name__)

IDLE_TIMEOUT_SECONDS = 300
SESSION_MAX_DURATION_SECONDS = 1800
PRUNE_INTERVAL_SECONDS = 30


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: dict[int, WebSocket] = {}
        self.active_sessions: dict[int, RealtimeAssessmentSession] = {}

    async def connect(
        self, *, websocket: WebSocket, user_id: int, sample_rate: int
    ) -> RealtimeAssessmentSession:
        await websocket.accept()

        session = RealtimeAssessmentSession(
            user_id=user_id,
            target_text="",
            sample_rate=sample_rate,
            audio_buffer=deque(),
            buffered_samples=0,
            received_samples=0,
            partial_transcript="",
            last_activity=normalize_datetime(datetime.now(UTC)),
            started_at=normalize_datetime(datetime.now(UTC)),
            processed_samples=0,
            last_sequence=None,
            inference_in_progress=False,
            inference_task=None,
            inference_error=None,
            message_metadata=[],
            scoring_windows=[],
        )

        self.active_connections[user_id] = websocket
        self.active_sessions[user_id] = session

        return session

    def disconnect(self, *, user_id: int) -> None:
        session = self.active_sessions.pop(user_id, None)

        if session is not None:
            if session.inference_task is not None and not session.inference_task.done():
                session.inference_task.cancel()

            session.audio_buffer.clear()
            session.message_metadata.clear()
            session.scoring_windows.clear()

        self.active_connections.pop(user_id, None)

    def prune_stale_connections(self) -> None:
        now = datetime.now(UTC)
        stale_ids = []

        for user_id, session in list(self.active_sessions.items()):
            idle_seconds = (now - session.last_activity).total_seconds()
            session_seconds = (now - session.started_at).total_seconds()

            if (
                idle_seconds > IDLE_TIMEOUT_SECONDS
                or session_seconds > SESSION_MAX_DURATION_SECONDS
            ):
                stale_ids.append(user_id)

        for user_id in stale_ids:
            logger.info("Pruning stale WebSocket connection for user %d", user_id)
            self.disconnect(user_id=user_id)

    async def run_pruning_loop(self) -> None:
        while True:
            try:
                await asyncio.sleep(PRUNE_INTERVAL_SECONDS)
                self.prune_stale_connections()
            except Exception:
                logger.exception("Error in pruning loop, continuing")

    async def send_json(self, *, user_id: int, payload: Any) -> None:
        websocket = self.active_connections.get(user_id)

        if websocket is None:
            return

        try:
            if isinstance(payload, msgspec.Struct):
                payload = msgspec.to_builtins(payload)

            await websocket.send_json(payload)

        except Exception:
            logger.exception("Failed to send JSON to user %d, disconnecting", user_id)
            self.disconnect(user_id=user_id)

    def get_session(self, *, user_id: int) -> RealtimeAssessmentSession | None:
        return self.active_sessions.get(user_id)


connection_manager = ConnectionManager()
