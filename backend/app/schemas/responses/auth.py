from __future__ import annotations

from msgspec import (
    Struct,
)


class AuthUserResponse(Struct, kw_only=True):
    id: int
    name: str
    username: str
    avatar_url: str


class AuthResponse(Struct, kw_only=True):
    token_type: str = "Bearer"
    access_token: str | None = None
    refresh_token: str | None = None
    user: AuthUserResponse | None = None
    mfa_required: bool = False
    temporary_token: str | None = None


class LogoutResponse(Struct, kw_only=True):
    success: bool
