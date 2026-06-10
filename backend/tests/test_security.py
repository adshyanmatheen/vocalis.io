from __future__ import annotations

import jwt
import pytest

from app.domain.auth.exceptions import (
    ExpiredAccessTokenError,
    InvalidAccessTokenError,
    InvalidNameError,
    InvalidPasswordError,
)
from app.domain.auth.security import (
    decode_access_token,
    generate_access_token,
    hash_refresh_token,
    validate_name,
    validate_password,
)


def test_generate_token() -> None:
    token = generate_access_token(user_id=1, session_id=1)

    assert isinstance(token, str)


def test_decode_token() -> None:
    token = generate_access_token(user_id=1, session_id=1)
    payload = decode_access_token(token)

    assert payload["user_id"] == 1
    assert payload["session_id"] == 1


def test_decode_token_with_invalid_signature() -> None:
    token = generate_access_token(user_id=1, session_id=1)
    parts = token.split(".")
    tampered_token = f"{parts[0]}.{parts[1]}.invalidsignature"

    with pytest.raises(InvalidAccessTokenError):
        decode_access_token(tampered_token)


def test_decode_expired_token() -> None:
    from datetime import UTC, datetime, timedelta

    from app.core.config import settings

    expired_payload = {
        "user_id": 1,
        "session_id": 1,
        "exp": datetime.now(UTC) - timedelta(hours=1),
    }
    expired_token = jwt.encode(
        expired_payload, settings.app.jwt_secret_key, algorithm="HS256"
    )

    with pytest.raises(ExpiredAccessTokenError):
        decode_access_token(expired_token)


def test_decode_token_with_missing_user_id() -> None:
    from app.core.config import settings

    payload = {"session_id": 1}
    token = jwt.encode(payload, settings.app.jwt_secret_key, algorithm="HS256")

    result = decode_access_token(token)

    assert result.get("user_id") is None


def test_hash_refresh_token_is_deterministic_and_non_reversible() -> None:
    refresh_token = "raw-refresh-token"
    token_hash = hash_refresh_token(refresh_token)

    assert token_hash == hash_refresh_token(refresh_token)
    assert token_hash != refresh_token
    assert len(token_hash) == 64


def test_validate_name_too_short() -> None:
    with pytest.raises(InvalidNameError):
        validate_name("A")


def test_validate_name_with_numbers() -> None:
    with pytest.raises(InvalidNameError):
        validate_name("John123")


def test_validate_name_valid() -> None:
    result = validate_name("John")
    assert result == "John"


def test_validate_password_too_short() -> None:
    with pytest.raises(InvalidPasswordError):
        validate_password("Ab1")


def test_validate_password_no_uppercase() -> None:
    with pytest.raises(InvalidPasswordError):
        validate_password("abcdefgh1")


def test_validate_password_no_lowercase() -> None:
    with pytest.raises(InvalidPasswordError):
        validate_password("ABCDEFGH1")


def test_validate_password_no_digit() -> None:
    with pytest.raises(InvalidPasswordError):
        validate_password("Abcdefgh")


def test_validate_password_valid() -> None:
    result = validate_password("Password123")
    assert result == "Password123"
