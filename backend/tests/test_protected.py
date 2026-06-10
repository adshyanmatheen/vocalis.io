from __future__ import annotations

from httpx import AsyncClient

PROTECTED_GET_ENDPOINTS = [
    "/api/v1/auth/me",
    "/api/v1/account/summary",
    "/api/v1/assessment/history",
]

PROTECTED_POST_ENDPOINTS = [
    "/api/v1/auth/mfa/setup",
    "/api/v1/auth/mfa/verify",
    "/api/v1/auth/mfa/disable",
    "/api/v1/auth/logout",
]


async def test_protected_route_requires_auth(async_client: AsyncClient) -> None:
    response = await async_client.get("/api/v1/auth/me")

    assert response.status_code in (401, 403)


async def test_all_protected_get_endpoints_require_auth(
    async_client: AsyncClient,
) -> None:
    for endpoint in PROTECTED_GET_ENDPOINTS:
        response = await async_client.get(endpoint)
        assert response.status_code in (
            401,
            403,
        ), f"{endpoint} should require authentication"


async def test_all_protected_post_endpoints_require_auth(
    async_client: AsyncClient,
) -> None:
    for endpoint in PROTECTED_POST_ENDPOINTS:
        response = await async_client.post(endpoint, json={})
        assert response.status_code in (
            401,
            403,
        ), f"{endpoint} should require authentication"


async def test_get_current_user(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.get(
        "/api/v1/auth/me",
    )

    assert response.status_code == 200
    data = response.json()
    assert "username" in data
    assert "avatar_url" in data
    assert "name" in data
    assert "id" in data
