from __future__ import annotations

from http.cookies import SimpleCookie

from litestar import WebSocket
from litestar.exceptions import NotAuthorizedException
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.auth.constants import ACCESS_TOKEN_COOKIE_NAME
from app.domain.auth.exceptions import (
    ExpiredAccessTokenError,
    InvalidAccessTokenError,
)
from app.domain.auth.repository import AuthRepository
from app.domain.auth.security import decode_access_token
from app.domain.database.models.user import User

auth_repository = AuthRepository()


def extract_cookie_token(websocket: WebSocket) -> str | None:
    cookies = getattr(websocket, "cookies", {})
    cookie_token = cookies.get(ACCESS_TOKEN_COOKIE_NAME)

    if cookie_token:
        return cookie_token

    cookie_header = websocket.headers.get("Cookie") or websocket.headers.get("cookie")

    if not cookie_header:
        return None

    parsed_cookie = SimpleCookie()
    parsed_cookie.load(cookie_header)
    cookie = parsed_cookie.get(ACCESS_TOKEN_COOKIE_NAME)

    return cookie.value if cookie else None


def extract_websocket_token(websocket: WebSocket) -> str | None:
    query_token = websocket.query_params.get("token")

    if query_token:
        return query_token

    authorization_header = websocket.headers.get("Authorization")

    if not authorization_header:
        return extract_cookie_token(websocket)

    if not authorization_header.startswith("Bearer "):
        return extract_cookie_token(websocket)

    return authorization_header.removeprefix("Bearer ").strip()


async def authenticate_websocket_user(
    *, websocket: WebSocket, database_session: AsyncSession
) -> User:
    token = extract_websocket_token(websocket)

    if not token:
        raise NotAuthorizedException("The WebSocket Authorization Token Is Missing.")

    try:
        payload = decode_access_token(token)

    except (ExpiredAccessTokenError, InvalidAccessTokenError) as error:
        raise NotAuthorizedException(str(error)) from error

    user_id = payload.get("user_id")

    if not user_id:
        raise NotAuthorizedException("The Token Payload Is Invalid.")

    user = await auth_repository.get_user_by_id(
        database_session=database_session,
        user_id=user_id,
    )

    if user is None:
        raise NotAuthorizedException("The User Has Not Been Found.")

    return user
