"""Architecture Analysis Domain Exceptions module.

Defines the exception hierarchy for architectural model definitions,
validations, and static analysis phases.
"""


class ArchitectureError(Exception):
    """Base exception class for all architecture domain errors."""

    pass


class ArchitectureAnalysisError(ArchitectureError):
    """Raised when an error occurs during architectural analysis processes."""

    pass


class ArchitectureModelError(ArchitectureError):
    """Raised when architectural layers or metrics are model-defined incorrectly."""

    pass


class ArchitectureValidationError(ArchitectureError):
    """Raised when architectural layering or validation constraints are violated."""

    pass
