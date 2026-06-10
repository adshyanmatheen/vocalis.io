from __future__ import annotations

from msgspec import (
    Struct,
)


class MFASetupRequest(Struct, kw_only=True):
    pass


class MFAVerifyRequest(Struct, kw_only=True):
    code: str

    def __post_init__(self) -> None:
        if not self.code.isdigit() or len(self.code) != 6:
            raise ValueError("code must be exactly 6 digits")


class MFALoginRequest(Struct, kw_only=True):
    temporary_token: str
    code: str

    def __post_init__(self) -> None:
        if not self.temporary_token.strip():
            raise ValueError("temporary_token is required")
        if not self.code.isdigit() or len(self.code) != 6:
            raise ValueError("code must be exactly 6 digits")


class MFADisableRequest(Struct, kw_only=True):
    code: str

    def __post_init__(self) -> None:
        if not self.code.isdigit() or len(self.code) != 6:
            raise ValueError("code must be exactly 6 digits")
