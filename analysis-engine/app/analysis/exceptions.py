"""AI Analysis Domain Exceptions module.

Defines custom exception classes for analysis domain configuration, validation,
and runtime execution issues.
"""


class AnalysisError(Exception):
    """Base exception class for all AI Analysis subsystem errors."""

    pass


class AnalysisValidationError(AnalysisError):
    """Raised when analysis configuration, models, or findings fail validation constraints."""

    pass


class AnalysisExecutionError(AnalysisError):
    """Raised when an active analyzer fails to complete its analysis run."""

    pass
