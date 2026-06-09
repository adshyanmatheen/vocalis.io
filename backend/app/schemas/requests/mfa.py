from __future__ import annotations

from msgspec import (
    Struct,
)


class MFASetupRequest(Struct, kw_only=True):
    pass


class MFAVerifyRequest(Struct, kw_only=True):
    code: str


class MFALoginRequest(Struct, kw_only=True):
    temporary_token: str
    code: str


class MFADisableRequest(Struct, kw_only=True):
    code: str
