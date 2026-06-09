from __future__ import annotations

from httpx import AsyncClient

from app.domain.database.models.phoneme_memory import PhonemeMemory
from app.domain.database.models.pronunciation_attempt import PronunciationAttempt
from app.domain.database.session import AsyncSessionLocal


async def test_account_summary_requires_authentication(
    async_client: AsyncClient,
) -> None:
    response = await async_client.get("/api/v1/account/summary")

    assert response.status_code == 401


async def test_account_summary_empty_state(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.get("/api/v1/account/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["user"]["name"] == "Adshyan"
    assert payload["activity"]["total_attempts"] == 0
    assert payload["activity"]["average_score"] == 0.0
    assert payload["activity"]["recent_attempts"] == []
    assert payload["progress"]["score_series"] == []
    assert payload["progress"]["performance_band_counts"] == {}
    assert payload["progress"]["recent_weak_phonemes"] == []
    assert payload["personalization"]["current_focus"] is None
    assert payload["personalization"]["focus_phonemes"] == []


async def test_account_summary_includes_activity_and_personalization(
    authenticated_client: AsyncClient,
) -> None:
    user_response = await authenticated_client.get("/api/v1/auth/me")
    user_response.raise_for_status()
    user_id = user_response.json()["id"]

    async with AsyncSessionLocal() as database_session:
        database_session.add_all(
            [
                PronunciationAttempt(
                    user_id=user_id,
                    target_text="The quick brown fox",
                    target_difficulty="intermediate",
                    overall_score=0.72,
                    performance_band="developing",
                    phoneme_results=[],
                    word_scores=[],
                    feedback_payload={},
                    weak_phonemes=["r", "th"],
                ),
                PronunciationAttempt(
                    user_id=user_id,
                    target_text="Bright birds bring berries",
                    target_difficulty="intermediate",
                    overall_score=0.88,
                    performance_band="strong",
                    phoneme_results=[],
                    word_scores=[],
                    feedback_payload={},
                    weak_phonemes=["r"],
                ),
                PhonemeMemory(
                    user_id=user_id,
                    phoneme="r",
                    total_occurrences=8,
                    weak_occurrences=5,
                    average_score=0.54,
                    average_severity_score=0.43,
                    recent_weighted_score=0.58,
                    common_error_types=["substitution"],
                    trend_direction="improving",
                    consistency_score=0.82,
                    trend_confidence=0.7,
                ),
            ]
        )
        await database_session.commit()

    response = await authenticated_client.get("/api/v1/account/summary")

    assert response.status_code == 200
    payload = response.json()
    assert payload["activity"]["total_attempts"] == 2
    assert payload["activity"]["average_score"] == 0.8
    assert payload["activity"]["best_score"] == 0.88
    assert payload["activity"]["latest_score"] in {0.72, 0.88}
    assert len(payload["activity"]["recent_attempts"]) == 2
    assert payload["progress"]["performance_band_counts"] == {
        "developing": 1,
        "strong": 1,
    }
    assert payload["progress"]["recent_weak_phonemes"][0] == {
        "phoneme": "r",
        "count": 2,
    }
    assert payload["personalization"]["current_focus"] == "r"
    assert payload["personalization"]["focus_phonemes"][0]["phoneme"] == "r"
    assert payload["personalization"]["focus_phonemes"][0]["weak_occurrences"] == 5
