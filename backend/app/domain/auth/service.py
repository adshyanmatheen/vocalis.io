from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.domain.auth.constants import (
    AUTH_RATE_LIMIT_ATTEMPTS,
    AUTH_RATE_LIMIT_WINDOW_SECONDS,
)
from app.domain.auth.exceptions import (
    AuthenticationRateLimitError,
    InvalidCredentialsError,
    InvalidSessionError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.domain.auth.mfa import (
    MFAService,
)
from app.domain.auth.models import (
    AuthenticatedUser,
    AuthenticationResult,
    LoginPayload,
    MFALoginChallenge,
    RegisterPayload,
)
from app.domain.auth.repository import (
    AuthRepository,
)
from app.domain.auth.security import (
    decode_access_token,
    generate_avatar_url,
    generate_username,
    hash_password,
    hash_refresh_token,
    validate_name,
    validate_password,
    verify_password,
)
from app.domain.auth.session import (
    AuthSessionService,
)


class AuthService:
    def __init__(
        self,
        repository: AuthRepository | None = None,
        session: AuthSessionService | None = None,
        mfa: MFAService | None = None,
    ) -> None:
        self.repository = repository or AuthRepository()
        self.session = session or AuthSessionService()
        self.mfa = mfa or MFAService()

    async def register_user(
        self,
        *,
        database_session: AsyncSession,
        payload: RegisterPayload,
    ) -> AuthenticationResult:
        validated_name = validate_name(payload.name)
        validated_password = validate_password(payload.password)
        username = generate_username()

        existing_user = await self.repository.get_user_by_username(
            database_session=database_session,
            username=username,
        )

        if existing_user is not None:
            raise UserAlreadyExistsError("The Username Generated Already Exists.")

        user = await self.repository.create_user(
            database_session=database_session,
            name=validated_name,
            username=username,
            avatar_url=generate_avatar_url(username),
            password_hash=await asyncio.to_thread(hash_password, validated_password),
        )

        return await self.session.issue_authentication_result(
            database_session=database_session,
            user=user,
        )

    async def login_user(
        self,
        *,
        database_session: AsyncSession,
        payload: LoginPayload,
    ) -> AuthenticationResult | MFALoginChallenge:
        await self.enforce_auth_rate_limit(
            database_session=database_session,
            identifier=payload.username,
        )

        user = await self.repository.get_user_by_username(
            database_session=database_session,
            username=payload.username,
        )

        if user is None:
            raise UserNotFoundError("The User Account Does Not Exist.")

        password_is_valid = await asyncio.to_thread(
            verify_password, password=payload.password, password_hash=user.password_hash
        )

        if not password_is_valid:
            raise InvalidCredentialsError("The Credentials Provided Are Invalid.")

        if user.mfa_enabled:
            if not user.mfa_secret:
                raise InvalidSessionError("MFA Is Enabled But Not Configured.")

            return await self.mfa.issue_challenge(
                database_session=database_session,
                user=user,
            )

        await self.clear_auth_rate_limit(
            database_session=database_session,
            identifier=payload.username,
        )

        return await self.session.issue_authentication_result(
            database_session=database_session,
            user=user,
        )

    async def logout_user(
        self,
        *,
        database_session: AsyncSession,
        session_token: str,
    ) -> None:
        await self.repository.delete_session(
            database_session=database_session,
            session_token=hash_refresh_token(session_token),
        )

    async def authenticate_user(
        self,
        *,
        database_session: AsyncSession,
        access_token: str,
    ) -> AuthenticatedUser:
        payload = decode_access_token(access_token)
        user_id = payload.get("user_id")

        if user_id is None:
            raise InvalidSessionError("The Access Token Is Invalid.")

        user = await self.repository.get_user_by_id(
            database_session=database_session,
            user_id=user_id,
        )

        if user is None:
            raise UserNotFoundError("The User Account Does Not Exist.")

        return self.session.build_authenticated_user(user)

    async def enforce_auth_rate_limit(
        self,
        *,
        database_session: AsyncSession,
        identifier: str,
    ) -> None:
        normalized_identifier = identifier.strip().lower()
        now = datetime.now(UTC)
        cutoff = now - timedelta(seconds=AUTH_RATE_LIMIT_WINDOW_SECONDS)

        await self.repository.delete_old_auth_attempts(
            database_session=database_session,
            cutoff=cutoff,
        )
        recent_attempts = await self.repository.count_recent_auth_attempts(
            database_session=database_session,
            identifier=normalized_identifier,
            cutoff=cutoff,
        )

        if recent_attempts >= AUTH_RATE_LIMIT_ATTEMPTS:
            raise AuthenticationRateLimitError(
                "There Have Been Too Many Authentication Attempts."
            )

        await self.repository.create_auth_attempt(
            database_session=database_session,
            identifier=normalized_identifier,
            attempted_at=now,
        )

    async def clear_auth_rate_limit(
        self,
        *,
        database_session: AsyncSession,
        identifier: str,
    ) -> None:
        await self.repository.delete_auth_attempts_by_identifier(
            database_session=database_session,
            identifier=identifier.strip().lower(),
        )
