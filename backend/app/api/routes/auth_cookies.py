from __future__ import annotations

from litestar.response import Response

from app.core.config import settings
from app.domain.auth.constants import (
    ACCESS_TOKEN_COOKIE_NAME,
    ACCESS_TOKEN_DURATION_MINUTES,
    REFRESH_TOKEN_COOKIE_NAME,
    REFRESH_TOKEN_DURATION_DAYS,
)


def set_auth_cookies(
    response: Response,
    *,
    access_token: str,
    refresh_token: str,
) -> None:
    cookie_secure = settings.app.environment == "production"
    same_site = "strict" if cookie_secure else "lax"

    response.set_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        value=access_token,
        httponly=True,
        secure=cookie_secure,
        samesite=same_site,
        max_age=ACCESS_TOKEN_DURATION_MINUTES * 60,
        path="/",
    )

    response.set_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=cookie_secure,
        samesite=same_site,
        max_age=REFRESH_TOKEN_DURATION_DAYS * 24 * 60 * 60,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key=ACCESS_TOKEN_COOKIE_NAME,
        path="/",
    )
    response.delete_cookie(
        key=REFRESH_TOKEN_COOKIE_NAME,
        path="/",
    )
