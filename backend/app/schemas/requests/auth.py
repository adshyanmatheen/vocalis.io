from __future__ import annotations

from msgspec import (
    Struct,
)


class RegisterRequest(Struct, kw_only=True):
    name: str
    password: str

    def __post_init__(self) -> None:
        if not 2 <= len(self.name) <= 32:
            raise ValueError("name must be 2–32 characters")
        if len(self.password) < 8:
            raise ValueError("password must be at least 8 characters")


class LoginRequest(Struct, kw_only=True):
    username: str
    password: str

    def __post_init__(self) -> None:
        if not self.username.strip():
            raise ValueError("username is required")
        if not self.password:
            raise ValueError("password is required")
