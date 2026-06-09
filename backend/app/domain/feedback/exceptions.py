from __future__ import annotations


class FeedbackError(Exception):
    pass


class FeedbackGenerationError(FeedbackError):
    pass


class FeedbackValidationError(FeedbackError):
    pass


class PersonalizationError(FeedbackError):
    pass


class PersonalizationPersistenceError(PersonalizationError):
    pass


class PersonalizationAnalysisError(PersonalizationError):
    pass


class FeedbackServiceError(FeedbackError):
    pass
