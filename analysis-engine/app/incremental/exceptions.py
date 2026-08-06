"""Incremental Analysis Domain Exceptions Module."""


class IncrementalAnalysisError(Exception):
    """Base exception class for all incremental analysis domain errors."""

    pass


class IncrementalAnalysisValidationError(IncrementalAnalysisError):
    """Exception raised when input models or DTO properties fail validation rules."""

    pass
