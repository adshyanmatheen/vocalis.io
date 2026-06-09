from __future__ import annotations

from litestar import (
    get,
    post,
)
from litestar.connection import Request
from litestar.exceptions import (
    ClientException,
    NotAuthorizedException,
)
from litestar.response import Response
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.api.routes.auth_cookies import clear_auth_cookies, set_auth_cookies
from app.domain.auth.constants import REFRESH_TOKEN_COOKIE_NAME
from app.domain.auth.exceptions import (
    AuthenticationError,
    InvalidCredentialsError,
    UserNotFoundError,
)
from app.domain.auth.models import (
    LoginPayload,
    MFALoginChallenge,
    RegisterPayload,
)
from app.domain.auth.service import (
    AuthService,
)
from app.domain.database.models.user import (
    User,
)
from app.schemas.requests.auth import (
    LoginRequest,
    RegisterRequest,
)
from app.schemas.responses.auth import (
    AuthResponse,
    AuthUserResponse,
    LogoutResponse,
)

auth_service = AuthService()


@post(
    path="/auth/register",
)
async def register_user(
    data: RegisterRequest, database_session: AsyncSession
) -> Response[AuthResponse]:
    try:
        authentication_result = await auth_service.register_user(
            database_session=(database_session),
            payload=(
                RegisterPayload(
                    name=(data.name),
                    password=(data.password),
                )
            ),
        )

    except AuthenticationError as error:
        raise (ClientException(str(error))) from error

    response = Response(
        AuthResponse(
            token_type="Bearer",
            user=(
                AuthUserResponse(
                    id=(authentication_result.user.id),
                    name=(authentication_result.user.name),
                    username=(authentication_result.user.username),
                    profile_picture_url=(authentication_result.user.avatar_url),
                )
            ),
        )
    )

    set_auth_cookies(
        response,
        access_token=authentication_result.access_token,
        refresh_token=authentication_result.refresh_token,
    )

    return response


@post(path="/auth/login")
async def login_user(
    data: LoginRequest, database_session: AsyncSession
) -> Response[AuthResponse] | AuthResponse:

    try:
        authentication_result = await auth_service.login_user(
            database_session=(database_session),
            payload=(
                LoginPayload(
                    username=(data.username),
                    password=(data.password),
                )
            ),
        )

    except (InvalidCredentialsError, UserNotFoundError) as error:
        raise (NotAuthorizedException(str(error))) from error

    except AuthenticationError as error:
        raise (ClientException(str(error))) from error

    if isinstance(authentication_result, MFALoginChallenge):
        return AuthResponse(
            mfa_required=True,
            temporary_token=(authentication_result.temporary_token),
        )

    response = Response(
        AuthResponse(
            token_type="Bearer",
            user=(
                AuthUserResponse(
                    id=(authentication_result.user.id),
                    name=(authentication_result.user.name),
                    username=(authentication_result.user.username),
                    profile_picture_url=(authentication_result.user.avatar_url),
                )
            ),
        )
    )

    set_auth_cookies(
        response,
        access_token=authentication_result.access_token,
        refresh_token=authentication_result.refresh_token,
    )

    return response


@get(path="/auth/me", sync_to_thread=False)
def get_current_user(authenticated_user: User) -> AuthUserResponse:

    return AuthUserResponse(
        id=(authenticated_user.id),
        name=(authenticated_user.name),
        username=(authenticated_user.username),
        profile_picture_url=(authenticated_user.avatar_url),
    )


@post(path="/auth/refresh")
async def refresh_user_session(
    request: Request,
    database_session: AsyncSession,
) -> Response[AuthResponse]:
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)
    if not refresh_token:
        raise NotAuthorizedException("The Refresh Token Is Missing.")

    authentication_result = await auth_service.session.refresh_authentication_result(
        database_session=database_session,
        refresh_token=refresh_token,
    )
    if authentication_result is None:
        raise NotAuthorizedException("The Refresh Session Is Invalid.")

    response = Response(
        AuthResponse(
            token_type="Bearer",
            user=AuthUserResponse(
                id=authentication_result.user.id,
                name=authentication_result.user.name,
                username=authentication_result.user.username,
                profile_picture_url=authentication_result.user.avatar_url,
            ),
        )
    )
    set_auth_cookies(
        response,
        access_token=authentication_result.access_token,
        refresh_token=authentication_result.refresh_token,
    )
    return response


@post(path="/auth/logout")
async def logout_user(
    request: Request,
    database_session: AsyncSession,
    authenticated_user: User,
) -> Response[LogoutResponse]:
    refresh_token = request.cookies.get(REFRESH_TOKEN_COOKIE_NAME)

    if refresh_token:
        await auth_service.logout_user(
            database_session=database_session,
            session_token=refresh_token,
        )

    response = Response(LogoutResponse(success=True))
    clear_auth_cookies(response)
    return response
