from __future__ import annotations


def import_database_models() -> None:
    from app.domain.database.models import auth_attempt as auth_attempt
    from app.domain.database.models import mfa_challenge as mfa_challenge
    from app.domain.database.models import phoneme_memory as phoneme_memory
    from app.domain.database.models import (
        pronunciation_attempt as pronunciation_attempt,
    )
    from app.domain.database.models import session as session
    from app.domain.database.models import user as user
