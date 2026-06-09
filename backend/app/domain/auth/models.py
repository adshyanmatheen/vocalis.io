from __future__ import annotations

from msgspec import Struct


class RegisterPayload(Struct, frozen=True):
    name: str
    password: str


class LoginPayload(Struct, frozen=True):
    username: str
    password: str


class AuthenticatedUser(Struct, frozen=True):
    id: int
    name: str
    username: str
    avatar_url: str
    created_at: str


class SessionRecord(Struct, frozen=True):
    id: int
    user_id: int
    session_token: str
    expires_at: str
    created_at: str


class AccessTokenPayload(Struct, frozen=True):
    user_id: int
    session_id: int
    expires_at: str


class AuthenticationResult(Struct, frozen=True):
    user: AuthenticatedUser
    session: SessionRecord
    access_token: str
    refresh_token: str


class MFALoginChallenge(Struct, frozen=True):
    mfa_required: bool
    temporary_token: str


class MFASetupResult(Struct, frozen=True):
    provisioning_uri: str
    mfa_enabled: bool
