from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

import numpy as np
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

TEST_DATABASE_DIR = Path(tempfile.mkdtemp(prefix="vocalis-tests-"))
TEST_DATABASE_PATH = TEST_DATABASE_DIR / "test.sqlite3"
BACKEND_ROOT = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(BACKEND_ROOT))

os.environ.setdefault("ENVIRONMENT", "testing")
os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DATABASE_PATH}"
os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-jwt-secret-key-with-at-least-thirty-two-bytes",
)
os.environ.setdefault("GROQ_API_KEY", "test-groq-api-key")
os.environ["LITESTAR_WARN_IMPLICIT_SYNC_TO_THREAD"] = "0"

from app.domain.database.init import initialize_database  # noqa: E402
from app.main import app  # noqa: E402


def pytest_collection_modifyitems(
    config: pytest.Config, items: list[pytest.Item]
) -> None:
    if config.option.markexpr:
        return

    skip_model = pytest.mark.skip(
        reason="Run model tests explicitly with pytest -m model"
    )

    for item in items:
        if "model" in item.keywords:
            item.add_marker(skip_model)


@pytest_asyncio.fixture(autouse=True)
async def initialized_database() -> None:
    await initialize_database()


@pytest_asyncio.fixture
async def async_client() -> AsyncClient:
    transport = ASGITransport(app=app)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest_asyncio.fixture
async def authenticated_client(async_client: AsyncClient) -> AsyncClient:
    register_response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "name": "Adshyan",
            "password": "Password123",
        },
    )
    register_response.raise_for_status()

    return async_client


@pytest.fixture
def synthetic_waveform() -> np.ndarray:
    sample_rate = 16_000
    duration_seconds = 1.0
    time_axis = np.linspace(
        0,
        duration_seconds,
        int(sample_rate * duration_seconds),
        endpoint=False,
    )

    return (0.2 * np.sin(2 * np.pi * 220 * time_axis)).astype(np.float32)


@pytest.fixture
def synthetic_target_text() -> str:
    return "The quick brown fox"
