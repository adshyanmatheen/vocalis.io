class AudioProcessingError(Exception):
    """This Exception Acts As The Shared Parent For All Audio-Related Runtime Failures"""


class AudioValidationError(AudioProcessingError):
    """This Exception Is Raised When Uploaded Audio Fails Validation Requirements."""


class AudioDecodingError(AudioProcessingError):
    """This Exception Is Raised When Raw Audio Bytes Cannot Be Decoded Safely."""
