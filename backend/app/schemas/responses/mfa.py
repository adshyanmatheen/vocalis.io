from __future__ import annotations

from msgspec import (
    Struct,
)

from app.schemas.responses.auth import (
    AuthUserResponse,
)


class MFASetupResponse(Struct, kw_only=True):
    provisioning_uri: str
    mfa_enabled: bool


class MFAVerifyResponse(Struct, kw_only=True):
    success: bool
    mfa_enabled: bool


class MFALoginResponse(Struct, kw_only=True):
    access_token: str | None = None
    refresh_token: str | None = None
    token_type: str = "Bearer"
    user: AuthUserResponse
    mfa_enabled: bool
