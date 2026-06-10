from __future__ import annotations


class AssessmentError(Exception):
    """Base exception for all assessment domain errors."""


class AudioProcessingError(AssessmentError):
    """Raised when assessment audio processing fails."""


class TranscriptionError(AssessmentError):
    """Raised when speech transcription fails."""


class WordAlignmentError(AssessmentError):
    """Raised when word-level alignment fails."""


class PronunciationAnalysisError(AssessmentError):
    """Raised when pronunciation analysis fails."""


class FeedbackGenerationError(AssessmentError):
    """Raised when assessment feedback generation fails."""


class PersonalizationError(AssessmentError):
    """Raised when personalization during assessment fails."""


class AssessmentPersistenceError(AssessmentError):
    """Raised when persisting assessment results fails."""


class InvalidAssessmentPayloadError(AssessmentError):
    """Raised when the assessment request payload is invalid."""
