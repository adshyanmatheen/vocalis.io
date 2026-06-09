from __future__ import annotations

from datetime import (
    UTC,
    datetime,
    timedelta,
)

from sqlalchemy.ext.asyncio import (
    AsyncSession,
)

from app.domain.auth.constants import (
    REFRESH_TOKEN_DURATION_DAYS,
)
from app.domain.auth.models import (
    AuthenticatedUser,
    AuthenticationResult,
    SessionRecord,
)
from app.domain.auth.repository import (
    AuthRepository,
)
from app.domain.auth.security import (
    generate_access_token,
    generate_refresh_token,
    hash_refresh_token,
)
from app.domain.database.models.user import (
    User,
)


class AuthSessionService:
    def __init__(self) -> None:
        self.repository = AuthRepository()

    def normalize_datetime(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)

        return value

    def build_authenticated_user(self, user: User) -> AuthenticatedUser:
        return AuthenticatedUser(
            id=user.id,
            name=user.name,
            username=user.username,
            avatar_url=user.avatar_url,
            created_at=str(user.created_at),
        )

    async def issue_authentication_result(
        self,
        *,
        database_session: AsyncSession,
        user: User,
    ) -> AuthenticationResult:
        refresh_token = generate_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_DURATION_DAYS)

        session = await self.repository.create_session(
            database_session=database_session,
            user_id=user.id,
            session_token=hash_refresh_token(refresh_token),
            expires_at=expires_at,
        )

        access_token = generate_access_token(
            user_id=user.id,
            session_id=session.id,
        )

        return AuthenticationResult(
            user=self.build_authenticated_user(user),
            session=SessionRecord(
                id=session.id,
                user_id=session.user_id,
                session_token=session.session_token,
                expires_at=str(session.expires_at),
                created_at=str(session.created_at),
            ),
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def refresh_authentication_result(
        self,
        *,
        database_session: AsyncSession,
        refresh_token: str,
    ) -> AuthenticationResult | None:
        session = await self.repository.get_session_by_token(
            database_session=database_session,
            session_token=hash_refresh_token(refresh_token),
        )
        if session is None:
            return None

        now = datetime.now(UTC)
        if self.normalize_datetime(session.expires_at) <= now:
            await self.repository.delete_session(
                database_session=database_session,
                session_token=hash_refresh_token(refresh_token),
            )
            return None

        user = await self.repository.get_user_by_id(
            database_session=database_session,
            user_id=session.user_id,
        )
        if user is None:
            await self.repository.delete_session(
                database_session=database_session,
                session_token=hash_refresh_token(refresh_token),
            )
            return None

        rotated_refresh_token = generate_refresh_token()
        expires_at = now + timedelta(days=REFRESH_TOKEN_DURATION_DAYS)
        session = await self.repository.replace_session_token(
            database_session=database_session,
            session=session,
            session_token=hash_refresh_token(rotated_refresh_token),
            expires_at=expires_at,
        )
        access_token = generate_access_token(
            user_id=user.id,
            session_id=session.id,
        )
        return AuthenticationResult(
            user=self.build_authenticated_user(user),
            session=SessionRecord(
                id=session.id,
                user_id=session.user_id,
                session_token=session.session_token,
                expires_at=str(session.expires_at),
                created_at=str(session.created_at),
            ),
            access_token=access_token,
            refresh_token=rotated_refresh_token,
        )
