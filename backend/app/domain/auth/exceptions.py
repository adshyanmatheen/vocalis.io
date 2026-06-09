from __future__ import annotations


class AuthenticationError(Exception):
    pass


class InvalidCredentialsError(AuthenticationError):
    pass


class InvalidNameError(AuthenticationError):
    pass


class InvalidPasswordError(AuthenticationError):
    pass


class UserAlreadyExistsError(AuthenticationError):
    pass


class UserNotFoundError(AuthenticationError):
    pass


class SessionExpiredError(AuthenticationError):
    pass


class InvalidSessionError(AuthenticationError):
    pass


class AuthenticationRateLimitError(AuthenticationError):
    pass


class MFARequiredError(AuthenticationError):
    pass


class InvalidMFAChallengeError(AuthenticationError):
    pass


class InvalidMFACodeError(AuthenticationError):
    pass


class InvalidAccessTokenError(Exception):
    pass


class ExpiredAccessTokenError(Exception):
    pass
