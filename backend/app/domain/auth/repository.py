from __future__ import annotations

from datetime import (
    datetime,
)

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.database.models.auth_attempt import AuthAttempt
from app.domain.database.models.mfa_challenge import MFAChallenge
from app.domain.database.models.session import Session
from app.domain.database.models.user import User
from app.domain.utils import normalize_datetime


class AuthRepository:
    async def create_user(
        self,
        *,
        database_session: AsyncSession,
        name: str,
        username: str,
        avatar_url: str,
        password_hash: str,
    ) -> User:
        user = User(
            name=name,
            username=username,
            avatar_url=avatar_url,
            password_hash=password_hash,
        )

        database_session.add(user)

        await database_session.commit()
        await database_session.refresh(user)

        return user

    async def get_user_by_id(
        self, *, database_session: AsyncSession, user_id: int
    ) -> User | None:
        statement = select(User).where(User.id == user_id)
        result = await database_session.execute(statement)

        return result.scalar_one_or_none()

    async def get_user_by_username(
        self, *, database_session: AsyncSession, username: str
    ) -> User | None:
        statement = select(User).where(User.username == username)
        result = await database_session.execute(statement)

        return result.scalar_one_or_none()

    async def create_session(
        self,
        *,
        database_session: AsyncSession,
        user_id: int,
        session_token: str,
        expires_at: datetime,
    ) -> Session:
        session = Session(
            user_id=user_id,
            session_token=session_token,
            expires_at=normalize_datetime(expires_at),
        )

        database_session.add(session)

        await database_session.commit()
        await database_session.refresh(session)
        return session

    async def get_session_by_token(
        self, *, database_session: AsyncSession, session_token: str
    ) -> Session | None:
        statement = select(Session).where(Session.session_token == session_token)
        result = await database_session.execute(statement)

        return result.scalar_one_or_none()

    async def get_session_by_id(
        self, *, database_session: AsyncSession, session_id: int
    ) -> Session | None:
        statement = select(Session).where(Session.id == session_id)
        result = await database_session.execute(statement)
        return result.scalar_one_or_none()

    async def replace_session_token(
        self,
        *,
        database_session: AsyncSession,
        session: Session,
        session_token: str,
        expires_at: datetime,
    ) -> Session:
        session.session_token = session_token
        session.expires_at = normalize_datetime(expires_at)
        database_session.add(session)
        await database_session.commit()
        await database_session.refresh(session)
        return session

    async def delete_session(
        self, *, database_session: AsyncSession, session_token: str
    ) -> None:
        statement = delete(Session).where(Session.session_token == session_token)

        await database_session.execute(statement)
        await database_session.commit()

    async def set_user_mfa_secret(
        self, *, database_session: AsyncSession, user: User, secret: str | None
    ) -> User:
        user.mfa_secret = secret

        database_session.add(user)
        await database_session.commit()
        await database_session.refresh(user)

        return user

    async def set_user_mfa_enabled(
        self, *, database_session: AsyncSession, user: User, enabled: bool
    ) -> User:
        user.mfa_enabled = enabled

        if not enabled:
            user.mfa_secret = None

        database_session.add(user)
        await database_session.commit()
        await database_session.refresh(user)

        return user

    async def create_mfa_challenge(
        self,
        *,
        database_session: AsyncSession,
        user_id: int,
        token_hash: str,
        expires_at: datetime,
    ) -> MFAChallenge:
        challenge = MFAChallenge(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=normalize_datetime(expires_at),
        )

        database_session.add(challenge)

        await database_session.commit()
        await database_session.refresh(challenge)

        return challenge

    async def get_mfa_challenge_by_token_hash(
        self, *, database_session: AsyncSession, token_hash: str
    ) -> MFAChallenge | None:
        statement = select(MFAChallenge).where(MFAChallenge.token_hash == token_hash)
        result = await database_session.execute(statement)

        return result.scalar_one_or_none()

    async def mark_mfa_challenge_used(
        self,
        *,
        database_session: AsyncSession,
        challenge: MFAChallenge,
        used_at: datetime,
    ) -> MFAChallenge:
        challenge.used_at = normalize_datetime(used_at)

        database_session.add(challenge)
        await database_session.commit()
        await database_session.refresh(challenge)

        return challenge

    async def delete_old_auth_attempts(
        self,
        *,
        database_session: AsyncSession,
        cutoff: datetime,
    ) -> None:
        cutoff = normalize_datetime(cutoff)
        statement = delete(AuthAttempt).where(AuthAttempt.attempted_at < cutoff)
        await database_session.execute(statement)
        await database_session.commit()

    async def count_recent_auth_attempts(
        self,
        *,
        database_session: AsyncSession,
        identifier: str,
        cutoff: datetime,
    ) -> int:
        cutoff = normalize_datetime(cutoff)
        statement = (
            select(func.count())
            .select_from(AuthAttempt)
            .where(AuthAttempt.identifier == identifier)
            .where(AuthAttempt.attempted_at >= cutoff)
        )
        result = await database_session.execute(statement)
        return int(result.scalar_one())

    async def create_auth_attempt(
        self,
        *,
        database_session: AsyncSession,
        identifier: str,
        attempted_at: datetime,
    ) -> AuthAttempt:
        attempt = AuthAttempt(
            identifier=identifier, attempted_at=normalize_datetime(attempted_at)
        )
        database_session.add(attempt)
        await database_session.commit()
        await database_session.refresh(attempt)
        return attempt

    async def delete_auth_attempts_by_identifier(
        self,
        *,
        database_session: AsyncSession,
        identifier: str,
    ) -> None:
        statement = delete(AuthAttempt).where(AuthAttempt.identifier == identifier)
        await database_session.execute(statement)
        await database_session.commit()
