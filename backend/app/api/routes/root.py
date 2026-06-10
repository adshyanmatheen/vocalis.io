from litestar import get

from app.schemas.responses.root import RootResponse


@get(
    path="/",
    operation_id="root",
    summary="Root Health Check",
    description="This Route Provides A Basic Health Check Endpoint That Returns The Application Name, Version, And Current Operational Status To Confirm The Service Is Running.",
    tags=["Root"],
    sync_to_thread=False,
)
def root() -> RootResponse:
    return RootResponse(
        name="vocalis.io",
        version="v1",
        status="online",
    )
