from __future__ import annotations

import random
import secrets
from datetime import UTC, datetime, timedelta
from hashlib import sha256

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.core.config import settings
from app.domain.auth.constants import (
    ACCESS_TOKEN_DURATION_MINUTES,
    DEFAULT_AVATAR_BACKGROUND_TYPE,
    DEFAULT_AVATAR_RADIUS,
    DEFAULT_AVATAR_SIZE,
    DICEBEAR_BASE_URL,
    INVALID_NAME_MESSAGE,
    NAME_PATTERN,
    PASSWORD_DIGIT_MESSAGE,
    PASSWORD_DIGIT_PATTERN,
    PASSWORD_LENGTH_MESSAGE,
    PASSWORD_LOWERCASE_MESSAGE,
    PASSWORD_LOWERCASE_PATTERN,
    PASSWORD_UPPERCASE_MESSAGE,
    PASSWORD_UPPERCASE_PATTERN,
    USERNAME_ADJECTIVES,
    USERNAME_ANIMALS,
)
from app.domain.auth.exceptions import (
    ExpiredAccessTokenError,
    InvalidAccessTokenError,
    InvalidNameError,
    InvalidPasswordError,
)

password_hasher = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)


def validate_name(name: str) -> str:
    normalized_name = name.strip()

    if not NAME_PATTERN.match(normalized_name):
        raise InvalidNameError(INVALID_NAME_MESSAGE)

    return normalized_name


def validate_password(password: str) -> str:
    if len(password) < 8:
        raise InvalidPasswordError(PASSWORD_LENGTH_MESSAGE)

    if not PASSWORD_UPPERCASE_PATTERN.search(password):
        raise InvalidPasswordError(PASSWORD_UPPERCASE_MESSAGE)

    if not PASSWORD_LOWERCASE_PATTERN.search(password):
        raise InvalidPasswordError(PASSWORD_LOWERCASE_MESSAGE)

    if not PASSWORD_DIGIT_PATTERN.search(password):
        raise InvalidPasswordError(PASSWORD_DIGIT_MESSAGE)

    return password


def hash_password(password: str) -> str:
    return password_hasher.hash(password)


def verify_password(*, password: str, password_hash: str) -> bool:
    try:
        return password_hasher.verify(password_hash, password)

    except VerifyMismatchError:
        return False


def generate_username() -> str:
    adjective = random.choice(USERNAME_ADJECTIVES)
    animal = random.choice(USERNAME_ANIMALS)
    suffix = secrets.randbelow(9999)

    return f"{adjective}_{animal}_{suffix}"


def generate_avatar_url(username: str) -> str:
    return (
        f"{DICEBEAR_BASE_URL}"
        f"?seed={username}"
        f"&backgroundType="
        f"{DEFAULT_AVATAR_BACKGROUND_TYPE}"
        f"&radius="
        f"{DEFAULT_AVATAR_RADIUS}"
        f"&size="
        f"{DEFAULT_AVATAR_SIZE}"
    )


def generate_refresh_token() -> str:
    return secrets.token_urlsafe(128)


def hash_refresh_token(refresh_token: str) -> str:
    return sha256(refresh_token.encode("utf-8")).hexdigest()


def generate_access_token(*, user_id: int, session_id: int) -> str:

    expires_at = datetime.now(UTC) + timedelta(minutes=(ACCESS_TOKEN_DURATION_MINUTES))

    payload = {
        "user_id": (user_id),
        "session_id": (session_id),
        "exp": (expires_at),
    }

    return jwt.encode(payload, settings.app.jwt_secret_key, algorithm="HS256")


def decode_access_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.app.jwt_secret_key, algorithms=["HS256"])

    except jwt.ExpiredSignatureError as error:
        raise (ExpiredAccessTokenError("The Access Token Has Expired")) from error

    except jwt.InvalidTokenError as error:
        raise (InvalidAccessTokenError("The Access Token Is Invalid.")) from error
