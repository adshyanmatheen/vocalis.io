from __future__ import annotations

from datetime import (
    UTC,
    datetime,
)

from litestar.connection import (
    Request,
)
from litestar.exceptions import (
    NotAuthorizedException,
)
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.domain.auth.constants import ACCESS_TOKEN_COOKIE_NAME
from app.domain.auth.exceptions import (
    ExpiredAccessTokenError,
    InvalidAccessTokenError,
    InvalidCredentialsError,
)
from app.domain.auth.repository import (
    AuthRepository,
)
from app.domain.auth.security import (
    decode_access_token,
)
from app.domain.database.models.user import (
    User,
)

auth_repository = AuthRepository()


def normalize_datetime(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)

    return value


async def provide_current_user(
    request: Request, database_session: AsyncSession
) -> User:
    authorization_header = request.headers.get("Authorization")

    token = None
    if authorization_header and authorization_header.startswith("Bearer "):
        token = authorization_header.removeprefix("Bearer ").strip()

    if not token:
        token = request.cookies.get(ACCESS_TOKEN_COOKIE_NAME)

    if not token:
        raise (NotAuthorizedException("The Authorization Header Is Missing."))

    try:
        payload = decode_access_token(token)

    except (
        ExpiredAccessTokenError,
        InvalidAccessTokenError,
        InvalidCredentialsError,
    ) as error:
        raise (NotAuthorizedException(str(error))) from error

    user_id = payload.get("user_id")
    session_id = payload.get("session_id")

    if not user_id:
        raise (NotAuthorizedException("The Token Payload Is Invalid."))
    if not session_id:
        raise (NotAuthorizedException("The Session Payload Is Invalid."))

    session = await auth_repository.get_session_by_id(
        database_session=database_session,
        session_id=session_id,
    )
    if session is None:
        raise (NotAuthorizedException("The Authentication Session Is Invalid."))
    if session.user_id != user_id:
        raise (NotAuthorizedException("The Session Does Not Match The User."))
    if normalize_datetime(session.expires_at) <= datetime.now(UTC):
        raise (NotAuthorizedException("The Authentication Session Has Expired."))

    user = await auth_repository.get_user_by_id(
        database_session=(database_session), user_id=user_id
    )

    if not user:
        raise (NotAuthorizedException("The User Has Not Been Found."))

    return user
