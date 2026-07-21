"""Static analysis exceptions module.

Defines the exception hierarchy for static analysis orchestrations and pipeline passes.
"""


class AnalysisError(Exception):
    """Base exception class for all static analysis domain errors."""

    pass


class AnalyzerExecutionError(AnalysisError):
    """Raised when an individual static analyzer pass fails during pipeline execution."""

    pass
