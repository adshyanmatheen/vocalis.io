class AlignmentError(Exception):
    """This Exception Acts As The Shared Parent For All Alignment Runtime Failures."""


class ModelInitializationError(AlignmentError):
    """This Exception Is Raised When Alignment Models Cannot Be Loaded Safely."""


class QuantizationError(AlignmentError):
    """This Exception Is Raised When Runtime Model Quantization Fails."""


class TargetTextNormalizationError(AlignmentError):
    """This Exception Is Raised When Target Text Contains Unsupported Alignment Tokens."""


class ViterbiAlignmentError(AlignmentError):
    """This Exception Is Raised When Sequence Alignment Decoding Fails."""
