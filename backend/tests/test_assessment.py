from __future__ import annotations

from httpx import AsyncClient

from app.domain.assessment.repository import AssessmentRepository
from app.domain.database.session import AsyncSessionLocal


async def test_assessment_history(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.get("/api/v1/assessment/history")

    assert response.status_code == 200
    payload = response.json()
    assert "attempts" in payload
    assert "total_attempts" in payload


async def test_placeholder_assessment_analyze_route_is_not_registered(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.post(
        "/api/v1/assessment/analyze",
        json={
            "target_text": "The quick brown fox",
        },
    )

    assert response.status_code == 404


async def test_get_phoneme_memories_by_user_and_phonemes(
    authenticated_client: AsyncClient,
) -> None:
    repository = AssessmentRepository()

    async with AsyncSessionLocal() as db_session:
        await repository.create_phoneme_memory(
            database_session=db_session,
            user_id=1,
            phoneme="AA",
            phoneme_score=0.85,
            severity_score=0.15,
            error_type="none",
        )
        await repository.create_phoneme_memory(
            database_session=db_session,
            user_id=1,
            phoneme="IY",
            phoneme_score=0.55,
            severity_score=0.45,
            error_type="distortion",
        )

        result = await repository.get_phoneme_memories_by_user_and_phonemes(
            database_session=db_session,
            user_id=1,
            phonemes=["AA", "IY"],
        )

        assert "AA" in result
        assert "IY" in result
        assert result["AA"].phoneme == "AA"
        assert result["AA"].average_score == 0.85
        assert result["IY"].phoneme == "IY"
        assert result["IY"].average_score == 0.55
        assert "ZZ" not in result

        partial = await repository.get_phoneme_memories_by_user_and_phonemes(
            database_session=db_session,
            user_id=1,
            phonemes=["AA"],
        )

        assert "AA" in partial
        assert "IY" not in partial

        empty = await repository.get_phoneme_memories_by_user_and_phonemes(
            database_session=db_session,
            user_id=1,
            phonemes=["ZZ"],
        )

        assert empty == {}
