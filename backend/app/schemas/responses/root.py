from msgspec import Struct


class RootResponse(Struct, kw_only=True):
    name: str
    version: str
    status: str
