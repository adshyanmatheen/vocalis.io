from __future__ import annotations

from app.domain.auth.security import (
    decode_access_token,
    generate_access_token,
    hash_refresh_token,
)


def test_generate_token() -> None:
    token = generate_access_token(user_id=1, session_id=1)

    assert isinstance(token, str)


def test_decode_token() -> None:
    token = generate_access_token(user_id=1, session_id=1)
    payload = decode_access_token(token)

    assert payload["user_id"] == 1
    assert payload["session_id"] == 1


def test_hash_refresh_token_is_deterministic_and_non_reversible() -> None:
    refresh_token = "raw-refresh-token"
    token_hash = hash_refresh_token(refresh_token)

    assert token_hash == hash_refresh_token(refresh_token)
    assert token_hash != refresh_token
    assert len(token_hash) == 64
