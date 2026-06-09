from __future__ import annotations

import pyotp

from app.domain.auth.constants import (
    MFA_CODE_VALID_WINDOW,
    MFA_ISSUER_NAME,
)


def generate_mfa_secret() -> str:
    return pyotp.random_base32()


def generate_mfa_uri(*, secret: str, username: str) -> str:
    return pyotp.TOTP(secret).provisioning_uri(
        name=MFA_ISSUER_NAME,
        issuer_name=MFA_ISSUER_NAME,
    )


def verify_mfa_code(*, secret: str, code: str) -> bool:
    normalized_code = code.strip().replace(" ", "")

    if not normalized_code.isdigit():
        return False

    return pyotp.TOTP(secret).verify(
        normalized_code,
        valid_window=MFA_CODE_VALID_WINDOW,
    )
