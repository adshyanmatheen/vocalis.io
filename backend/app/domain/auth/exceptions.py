from __future__ import annotations


class AuthenticationError(Exception):
    """Base exception for all authentication domain errors."""


class InvalidCredentialsError(AuthenticationError):
    """Raised when login credentials are invalid."""


class InvalidNameError(AuthenticationError):
    """Raised when the provided name fails validation."""


class InvalidPasswordError(AuthenticationError):
    """Raised when the provided password fails validation."""


class UserAlreadyExistsError(AuthenticationError):
    """Raised when attempting to register a duplicate user."""


class UserNotFoundError(AuthenticationError):
    """Raised when a user is not found."""


class SessionExpiredError(AuthenticationError):
    """Raised when a session token has expired."""


class InvalidSessionError(AuthenticationError):
    """Raised when a session token is invalid."""


class AuthenticationRateLimitError(AuthenticationError):
    """Raised when authentication rate limit is exceeded."""


class MFARequiredError(AuthenticationError):
    """Raised when MFA is required but not yet verified."""


class InvalidMFAChallengeError(AuthenticationError):
    """Raised when the MFA challenge is invalid or expired."""


class InvalidMFACodeError(AuthenticationError):
    """Raised when the MFA verification code is incorrect."""


class InvalidAccessTokenError(Exception):
    """Raised when an access token is malformed or invalid."""


class ExpiredAccessTokenError(Exception):
    """Raised when an access token has expired."""
