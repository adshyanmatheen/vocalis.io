from __future__ import annotations

import pyotp

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
