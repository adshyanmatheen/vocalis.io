from __future__ import annotations

import pyotp
from httpx import AsyncClient

from app.domain.auth.totp import generate_mfa_secret, verify_mfa_code


def test_generate_secret() -> None:
    secret = generate_mfa_secret()

    assert isinstance(secret, str)
    assert secret


def test_verify_code() -> None:
    secret = generate_mfa_secret()
    code = pyotp.TOTP(secret).now()

    result = verify_mfa_code(secret=secret, code=code)

    assert result is True


async def test_mfa_setup_returns_provisioning_uri(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.post("/api/v1/auth/mfa/setup")
    assert response.status_code in (200, 201)
    data = response.json()
    assert "provisioning_uri" in data
    assert data["mfa_enabled"] is False


async def test_mfa_verify_with_invalid_code_returns_401(
    authenticated_client: AsyncClient,
) -> None:
    await authenticated_client.post("/api/v1/auth/mfa/setup")
    response = await authenticated_client.post(
        "/api/v1/auth/mfa/verify", json={"code": "000000"}
    )
    assert response.status_code == 401


async def test_mfa_disable_without_setup_succeeds(
    authenticated_client: AsyncClient,
) -> None:
    response = await authenticated_client.post(
        "/api/v1/auth/mfa/disable", json={"code": "000000"}
    )
    assert response.status_code in (200, 201)
    assert response.json()["mfa_enabled"] is False


async def test_mfa_verify_and_disable_flow(
    authenticated_client: AsyncClient,
) -> None:
    setup_response = await authenticated_client.post("/api/v1/auth/mfa/setup")
    assert setup_response.status_code in (200, 201)
    secret_uri = setup_response.json()["provisioning_uri"]

    import re

    secret_match = re.search(r"secret=([A-Z0-9]+)", secret_uri)
    assert secret_match is not None
    secret = secret_match.group(1)
    valid_code = pyotp.TOTP(secret).now()

    verify_response = await authenticated_client.post(
        "/api/v1/auth/mfa/verify", json={"code": valid_code}
    )
    assert verify_response.status_code in (200, 201)
    assert verify_response.json()["mfa_enabled"] is True

    new_code = pyotp.TOTP(secret).now()
    disable_response = await authenticated_client.post(
        "/api/v1/auth/mfa/disable", json={"code": new_code}
    )
    assert disable_response.status_code in (200, 201)
    assert disable_response.json()["mfa_enabled"] is False
