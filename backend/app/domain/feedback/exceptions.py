from __future__ import annotations


class FeedbackError(Exception):
    """Base exception for all feedback domain errors."""


class FeedbackGenerationError(FeedbackError):
    """Raised when feedback text generation fails."""


class FeedbackValidationError(FeedbackError):
    """Raised when generated feedback fails validation."""


class PersonalizationError(FeedbackError):
    """Base exception for personalization-related errors."""


class PersonalizationPersistenceError(PersonalizationError):
    """Raised when storing personalization data fails."""


class PersonalizationAnalysisError(PersonalizationError):
    """Raised when personalization analysis fails."""


class FeedbackServiceError(FeedbackError):
    """Raised when the feedback service encounters an unexpected error."""
