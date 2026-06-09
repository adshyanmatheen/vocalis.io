from __future__ import annotations

from msgspec import (
    Struct,
)


class RegisterRequest(Struct, kw_only=True):
    name: str
    password: str


class LoginRequest(Struct, kw_only=True):
    username: str
    password: str
