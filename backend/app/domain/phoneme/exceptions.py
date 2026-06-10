class PhonemeError(Exception):
    """This Exception Acts As The Shared Parent For All Phoneme Domain Failures."""


class PhonemeModelError(PhonemeError):
    """This Exception Is Raised When The Phoneme Recognition Model Fails To Load, Initialize, Or Execute Inference."""


class PhonemeInferenceError(PhonemeError):
    """This Exception Is Raised When Runtime Phoneme Inference Execution Fails During Audio Processing."""


class PhonemeDecodingError(PhonemeError):
    """This Exception Is Raised When Predicted Phoneme Tokens Cannot Be Decoded Into Structured Phoneme Segments."""


class PhonemizationError(PhonemeError):
    """This Exception Is Raised When Grapheme-To-Phoneme Conversion Fails During Linguistic Processing."""


class PhonemeSegmentationError(PhonemeError):
    """This Exception Is Raised When Expected Or Predicted Phoneme Segments Cannot Be Constructed Correctly."""


class PhonemeMatchingError(PhonemeError):
    """This Exception Is Raised When Expected And Predicted Phoneme Segments Cannot Be Matched Reliably."""


class PronunciationScoringError(PhonemeError):
    """This Exception Is Raised When Pronunciation Confidence Or Severity Scoring Fails."""


class PhonemeScoringError(PhonemeError):
    """This Exception Is Raised When Pronunciation Scoring Logic, Performance Band Classification, Or Phoneme Severity Evaluation Fails."""
