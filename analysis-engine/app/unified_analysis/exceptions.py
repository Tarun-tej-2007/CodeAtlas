"""Unified Analysis Exceptions Module."""


class UnifiedAnalysisError(Exception):
    """Base class for all exceptions in the Unified Analysis subsystem."""

    pass


class UnifiedAnalysisAggregationError(UnifiedAnalysisError):
    """Raised when there is an error during aggregation of analysis outputs."""

    pass
