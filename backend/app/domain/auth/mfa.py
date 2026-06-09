from __future__ import annotations

import hashlib
import secrets
from datetime import (
    UTC,
    datetime,
    timedelta,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.domain.auth.constants import (
    MFA_CHALLENGE_DURATION_MINUTES,
    MFA_RATE_LIMIT_ATTEMPTS,
    MFA_RATE_LIMIT_WINDOW_SECONDS,
)
from app.domain.auth.exceptions import (
    AuthenticationRateLimitError,
    InvalidMFAChallengeError,
    InvalidMFACodeError,
    UserNotFoundError,
)
from app.domain.auth.models import (
    AuthenticationResult,
    MFALoginChallenge,
    MFASetupResult,
)
from app.domain.auth.repository import (
    AuthRepository,
)
from app.domain.auth.session import (
    AuthSessionService,
)
from app.domain.auth.totp import (
    generate_mfa_secret,
    generate_mfa_uri,
    verify_mfa_code,
)
from app.domain.database.models.user import (
    User,
)


class MFAService:
    def __init__(
        self,
        repository: AuthRepository | None = None,
        session: AuthSessionService | None = None,
    ) -> None:
        self.repository = repository or AuthRepository()
        self.session = session or AuthSessionService()

    def hash_temporary_token(self, temporary_token: str) -> str:
        return hashlib.sha256(temporary_token.encode("utf-8")).hexdigest()

    def normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)

        return value

    async def issue_challenge(
        self,
        *,
        database_session: AsyncSession,
        user: User,
    ) -> MFALoginChallenge:
        temporary_token = secrets.token_urlsafe(64)
        expires_at = datetime.now(UTC) + timedelta(
            minutes=MFA_CHALLENGE_DURATION_MINUTES
        )

        await self.repository.create_mfa_challenge(
            database_session=database_session,
            user_id=user.id,
            token_hash=self.hash_temporary_token(temporary_token),
            expires_at=expires_at,
        )

        return MFALoginChallenge(
            mfa_required=True,
            temporary_token=temporary_token,
        )

    async def setup_mfa(
        self,
        *,
        database_session: AsyncSession,
        user: User,
    ) -> MFASetupResult:
        secret = generate_mfa_secret()
        user = await self.repository.set_user_mfa_secret(
            database_session=database_session,
            user=user,
            secret=secret,
        )

        return MFASetupResult(
            provisioning_uri=generate_mfa_uri(
                secret=secret,
                username=user.username,
            ),
            mfa_enabled=user.mfa_enabled,
        )

    async def verify_mfa_setup(
        self,
        *,
        database_session: AsyncSession,
        user: User,
        code: str,
    ) -> bool:
        if not user.mfa_secret:
            raise InvalidMFACodeError("MFA Has Not Been Set Up.")

        await self.enforce_mfa_rate_limit(
            database_session=database_session,
            identifier=f"mfa:setup:{user.id}",
        )

        if not verify_mfa_code(secret=user.mfa_secret, code=code):
            raise InvalidMFACodeError("The MFA Code Is Invalid.")

        await self.repository.set_user_mfa_enabled(
            database_session=database_session,
            user=user,
            enabled=True,
        )

        return True

    async def complete_mfa_login(
        self,
        *,
        database_session: AsyncSession,
        temporary_token: str,
        code: str,
    ) -> AuthenticationResult:
        challenge = await self.repository.get_mfa_challenge_by_token_hash(
            database_session=database_session,
            token_hash=self.hash_temporary_token(temporary_token),
        )

        now = datetime.now(UTC)

        if challenge is None:
            raise InvalidMFAChallengeError("The MFA Challenge Is Invalid.")

        if challenge.used_at is not None:
            raise InvalidMFAChallengeError("The MFA Challenge Has Already Been Used.")

        if self.normalize_datetime(challenge.expires_at) <= now:
            raise InvalidMFAChallengeError("The MFA Challenge Has Expired.")

        user = await self.repository.get_user_by_id(
            database_session=database_session,
            user_id=challenge.user_id,
        )

        if user is None:
            raise UserNotFoundError("The User Account Does Not Exist.")

        if not user.mfa_enabled or not user.mfa_secret:
            raise InvalidMFAChallengeError("MFA Is Not Enabled For This User.")

        await self.enforce_mfa_rate_limit(
            database_session=database_session,
            identifier=f"mfa:login:{user.id}",
        )

        if not verify_mfa_code(secret=user.mfa_secret, code=code):
            raise InvalidMFACodeError("The MFA Code Is Invalid.")

        await self.repository.mark_mfa_challenge_used(
            database_session=database_session,
            challenge=challenge,
            used_at=now,
        )

        return await self.session.issue_authentication_result(
            database_session=database_session,
            user=user,
        )

    async def disable_mfa(
        self,
        *,
        database_session: AsyncSession,
        user: User,
        code: str,
    ) -> bool:
        if not user.mfa_enabled or not user.mfa_secret:
            return True

        await self.enforce_mfa_rate_limit(
            database_session=database_session,
            identifier=f"mfa:disable:{user.id}",
        )

        if not verify_mfa_code(secret=user.mfa_secret, code=code):
            raise InvalidMFACodeError("The MFA Code Is Invalid.")

        await self.repository.set_user_mfa_enabled(
            database_session=database_session,
            user=user,
            enabled=False,
        )

        return True

    async def enforce_mfa_rate_limit(
        self,
        *,
        database_session: AsyncSession,
        identifier: str,
    ) -> None:
        now = datetime.now(UTC)
        cutoff = now - timedelta(seconds=MFA_RATE_LIMIT_WINDOW_SECONDS)
        await self.repository.delete_old_auth_attempts(
            database_session=database_session,
            cutoff=cutoff,
        )
        recent_attempts = await self.repository.count_recent_auth_attempts(
            database_session=database_session,
            identifier=identifier,
            cutoff=cutoff,
        )

        if recent_attempts >= MFA_RATE_LIMIT_ATTEMPTS:
            raise AuthenticationRateLimitError("There Have Been Too Many MFA Attempts.")

        await self.repository.create_auth_attempt(
            database_session=database_session,
            identifier=identifier,
            attempted_at=now,
        )
