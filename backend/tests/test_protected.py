from __future__ import annotations

from httpx import AsyncClient


async def test_protected_route_requires_auth(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/auth/me")

    assert response.status_code in (401, 403)


async def test_get_current_user(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == 200
    assert "username" in response.json()
