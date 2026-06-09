class TargetError(Exception):
    """This Exception Acts As The Shared Parent For All Target Domain Failures."""


class TargetRepositoryError(TargetError):
    """This Exception Is Raised When Target Exercises Cannot Be Loaded Or Retrieved."""


class TargetValidationError(TargetError):
    """This Exception Is Raised When Target Exercise Data Fails Validation Rules."""


class TargetSelectionError(TargetError):
    """This Exception Is Raised When Adaptive Target Selection Fails."""


class TargetNormalizationError(TargetError):
    """This Exception Is Raised When Target Text Normalization Fails."""


class TargetGenerationError(TargetError):
    """This Exception Is Raised When Dynamic Target Exercise Generation Fails."""
