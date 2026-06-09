from __future__ import annotations

from litestar.di import Provide

from app.domain.database.models.user import (
    User,
)


def require_authenticated_user(
    current_user: User,
) -> User:
    return current_user


require_authenticated_user_provide = Provide(
    require_authenticated_user, sync_to_thread=False
)
