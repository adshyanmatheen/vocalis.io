from __future__ import annotations

from litestar import (
    post,
)
from litestar.exceptions import (
    ClientException,
    NotAuthorizedException,
)
from litestar.response import Response
from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.api.routes.auth_cookies import set_auth_cookies
from app.domain.auth.exceptions import (
    AuthenticationError,
    InvalidMFAChallengeError,
    InvalidMFACodeError,
)
from app.domain.auth.mfa import (
    MFAService,
)
from app.domain.database.models.user import (
    User,
)
from app.schemas.requests.mfa import (
    MFADisableRequest,
    MFALoginRequest,
    MFAVerifyRequest,
)
from app.schemas.responses.auth import (
    AuthUserResponse,
)
from app.schemas.responses.mfa import (
    MFALoginResponse,
    MFASetupResponse,
    MFAVerifyResponse,
)

mfa = MFAService()


@post(path="/auth/mfa/setup")
async def setup_mfa(
    database_session: AsyncSession,
    authenticated_user: User,
) -> MFASetupResponse:
    try:
        setup_result = await mfa.setup_mfa(
            database_session=(database_session),
            user=(authenticated_user),
        )

    except AuthenticationError as error:
        raise (ClientException(str(error))) from error

    return MFASetupResponse(
        provisioning_uri=(setup_result.provisioning_uri),
        mfa_enabled=(setup_result.mfa_enabled),
    )


@post(path="/auth/mfa/verify")
async def verify_mfa(
    data: MFAVerifyRequest,
    database_session: AsyncSession,
    authenticated_user: User,
) -> MFAVerifyResponse:
    try:
        await mfa.verify_mfa_setup(
            database_session=(database_session),
            user=(authenticated_user),
            code=(data.code),
        )

    except InvalidMFACodeError as error:
        raise (NotAuthorizedException(str(error))) from error

    except AuthenticationError as error:
        raise (ClientException(str(error))) from error

    return MFAVerifyResponse(
        success=True,
        mfa_enabled=True,
    )


@post(path="/auth/mfa/login")
async def login_with_mfa(
    data: MFALoginRequest,
    database_session: AsyncSession,
) -> Response[MFALoginResponse]:
    try:
        authentication_result = await mfa.complete_mfa_login(
            database_session=(database_session),
            temporary_token=(data.temporary_token),
            code=(data.code),
        )

    except (InvalidMFAChallengeError, InvalidMFACodeError) as error:
        raise (NotAuthorizedException(str(error))) from error

    except AuthenticationError as error:
        raise (ClientException(str(error))) from error

    response = Response(
        MFALoginResponse(
            user=(
                AuthUserResponse(
                    id=(authentication_result.user.id),
                    name=(authentication_result.user.name),
                    username=(authentication_result.user.username),
                    profile_picture_url=(authentication_result.user.avatar_url),
                )
            ),
            mfa_enabled=True,
        )
    )

    set_auth_cookies(
        response,
        access_token=authentication_result.access_token,
        refresh_token=authentication_result.refresh_token,
    )

    return response


@post(path="/auth/mfa/disable")
async def disable_mfa(
    data: MFADisableRequest,
    database_session: AsyncSession,
    authenticated_user: User,
) -> MFAVerifyResponse:
    try:
        await mfa.disable_mfa(
            database_session=(database_session),
            user=(authenticated_user),
            code=(data.code),
        )

    except InvalidMFACodeError as error:
        raise (NotAuthorizedException(str(error))) from error

    except AuthenticationError as error:
        raise (ClientException(str(error))) from error

    return MFAVerifyResponse(
        success=True,
        mfa_enabled=False,
    )
