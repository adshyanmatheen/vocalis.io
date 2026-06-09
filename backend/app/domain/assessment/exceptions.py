from __future__ import annotations


class AssessmentError(Exception):
    pass


class AudioProcessingError(AssessmentError):
    pass


class TranscriptionError(AssessmentError):
    pass


class WordAlignmentError(AssessmentError):
    pass


class PronunciationAnalysisError(AssessmentError):
    pass


class FeedbackGenerationError(AssessmentError):
    pass


class PersonalizationError(AssessmentError):
    pass


class AssessmentPersistenceError(AssessmentError):
    pass


class InvalidAssessmentPayloadError(AssessmentError):
    pass
