"""Incremental Analysis Domain Exceptions Module."""


class IncrementalAnalysisError(Exception):
    """Base exception class for all incremental analysis domain errors."""

    pass


class IncrementalAnalysisValidationError(IncrementalAnalysisError):
    """Exception raised when input models or DTO properties fail validation rules."""

    pass


class IncrementalAnalysisPersistenceError(IncrementalAnalysisError):
    """Exception raised when database or storage actions fail."""

    pass


class IncrementalAnalysisFileSystemError(IncrementalAnalysisError):
    """Exception raised when files cannot be accessed or read on disk."""

    pass
