from __future__ import annotations

from httpx import AsyncClient

from app.domain.auth.constants import AUTH_RATE_LIMIT_ATTEMPTS


async def test_register_user(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "name": "Adshyan",
            "password": "Password123",
        },
    )

    assert response.status_code == 201
    data = response.json()
    assert response.cookies.get("access_token")
    assert response.cookies.get("refresh_token")
    assert data["user"]["username"]


async def test_login_user(async_client: AsyncClient) -> None:
    register_response = await async_client.post(
        "/api/v1/auth/register",
        json={
            "name": "Adshyan",
            "password": "Password123",
        },
    )
    username = register_response.json()["user"]["username"]

    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "username": username,
            "password": "Password123",
        },
    )

    assert response.status_code in (200, 201)
    assert response.cookies.get("access_token")


async def test_invalid_login(async_client: AsyncClient) -> None:
    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "username": "invalid",
            "password": "invalid",
        },
    )

    assert response.status_code in (400, 401)


async def test_login_rate_limit_is_enforced(async_client: AsyncClient) -> None:
    for _ in range(AUTH_RATE_LIMIT_ATTEMPTS):
        response = await async_client.post(
            "/api/v1/auth/login",
            json={
                "username": "rate_limit_target",
                "password": "invalid",
            },
        )
        assert response.status_code in (400, 401)

    response = await async_client.post(
        "/api/v1/auth/login",
        json={
            "username": "rate_limit_target",
            "password": "invalid",
        },
    )

    assert response.status_code == 400
    assert "Too Many Authentication Attempts" in response.text
