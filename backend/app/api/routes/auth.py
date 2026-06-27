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
from app.core.config import settings
from app.core.rate_limiter import register_limiter
from app.domain.audit.service import log_audit_event
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
    operation_id="registerUser",
    summary="Register A New User",
    description="This Route Creates A New User Account With The Provided Name And Password. On Success, Returns Authentication Tokens Via Both The Response Body And HttpOnly Cookies. Rate Limited To 5 Requests Per 60 Seconds Per IP Address.",
    tags=["Authentication"],
)
async def register_user(
    request: Request,
    data: RegisterRequest,
    database_session: AsyncSession,
) -> Response[AuthResponse]:
    if settings.app.environment != "testing":
        client_ip = request.client.host if request.client else "unknown"
        rate_limit = await register_limiter.check(client_ip)
        request.state.rate_limit = rate_limit
        if rate_limit.remaining <= 0:
            raise ClientException(
                "Too many registration attempts. Please try again later.",
                headers={
                    "X-RateLimit-Limit": str(rate_limit.limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(rate_limit.reset_at),
                },
            )
        await register_limiter.record(client_ip)
        request.state.rate_limit = await register_limiter.check(client_ip)
    try:
        authentication_result = await auth_service.register_user(
            database_session=database_session,
            payload=(
                RegisterPayload(
                    name=data.name,
                    password=data.password,
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
                    id=authentication_result.user.id,
                    name=authentication_result.user.name,
                    username=authentication_result.user.username,
                    avatar_url=authentication_result.user.avatar_url,
                )
            ),
        )
    )

    set_auth_cookies(
        response,
        access_token=authentication_result.access_token,
        refresh_token=authentication_result.refresh_token,
    )

    await log_audit_event(
        database_session=database_session,
        action="auth.register",
        actor_id=authentication_result.user.id,
        resource_type="user",
        resource_id=authentication_result.user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return response


@post(
    path="/auth/login",
    operation_id="loginUser",
    summary="Login With Credentials",
    description="This Route Authenticates A User Using Their Username And Password. If Multi-Factor Authentication Is Enabled, Returns A Temporary Token And An MFA Required Flag Instead Of Full Authentication Tokens. On Successful Authentication, Sets Access And Refresh Tokens As HttpOnly Cookies.",
    tags=["Authentication"],
)
async def login_user(
    request: Request,
    data: LoginRequest,
    database_session: AsyncSession,
) -> Response[AuthResponse] | AuthResponse:

    try:
        authentication_result = await auth_service.login_user(
            database_session=database_session,
            payload=(
                LoginPayload(
                    username=data.username,
                    password=data.password,
                )
            ),
        )

    except (InvalidCredentialsError, UserNotFoundError) as error:
        await log_audit_event(
            database_session=database_session,
            action="auth.login.failed",
            resource_type="user",
            resource_id=data.username,
            details={"reason": str(error)},
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        raise (NotAuthorizedException(str(error))) from error

    except AuthenticationError as error:
        raise (ClientException(str(error))) from error

    if isinstance(authentication_result, MFALoginChallenge):
        await log_audit_event(
            database_session=database_session,
            action="auth.login.mfa_challenge",
            resource_type="user",
            resource_id=authentication_result.temporary_token,
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
        )
        return AuthResponse(
            mfa_required=True,
            temporary_token=authentication_result.temporary_token,
        )

    response = Response(
        AuthResponse(
            token_type="Bearer",
            user=(
                AuthUserResponse(
                    id=authentication_result.user.id,
                    name=authentication_result.user.name,
                    username=authentication_result.user.username,
                    avatar_url=authentication_result.user.avatar_url,
                )
            ),
        )
    )

    set_auth_cookies(
        response,
        access_token=authentication_result.access_token,
        refresh_token=authentication_result.refresh_token,
    )

    await log_audit_event(
        database_session=database_session,
        action="auth.login",
        actor_id=authentication_result.user.id,
        resource_type="user",
        resource_id=authentication_result.user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return response


@get(
    path="/auth/me",
    operation_id="getCurrentUser",
    summary="Get Authenticated User",
    description="This Route Retrieves The Profile Information For The Currently Authenticated User, Including Their ID, Name, Username, And Profile Picture URL.",
    tags=["Authentication"],
    sync_to_thread=False,
)
def get_current_user(authenticated_user: User) -> AuthUserResponse:

    return AuthUserResponse(
        id=authenticated_user.id,
        name=authenticated_user.name,
        username=authenticated_user.username,
        avatar_url=authenticated_user.avatar_url,
    )


@post(
    path="/auth/refresh",
    operation_id="refreshUserSession",
    summary="Refresh Access Token",
    description="This Route Exchanges A Valid Refresh Token From The Request Cookies For A New Access Token And Refresh Token Pair. Returns A 401 Unauthorized Error If The Refresh Token Is Missing, Expired, Or Invalid.",
    tags=["Authentication"],
)
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
                avatar_url=authentication_result.user.avatar_url,
            ),
        )
    )
    set_auth_cookies(
        response,
        access_token=authentication_result.access_token,
        refresh_token=authentication_result.refresh_token,
    )

    await log_audit_event(
        database_session=database_session,
        action="auth.refresh",
        actor_id=authentication_result.user.id,
        resource_type="session",
        resource_id=authentication_result.user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return response


@post(
    path="/auth/logout",
    operation_id="logoutUser",
    summary="Logout And Clear Session",
    description="This Route Invalidates The Refresh Token In The Database And Clears Both The Access And Refresh Token Cookies From The Response, Effectively Ending The User Session.",
    tags=["Authentication"],
)
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

    await log_audit_event(
        database_session=database_session,
        action="auth.logout",
        actor_id=authenticated_user.id,
        resource_type="session",
        resource_id=authenticated_user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )

    return response
