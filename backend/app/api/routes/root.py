from litestar import get

from app.schemas.responses.root import RootResponse


@get(path="/", sync_to_thread=False)
def root() -> RootResponse:
    return RootResponse(
        name="vocalis.io",
        version="v1",
        status="online",
    )
