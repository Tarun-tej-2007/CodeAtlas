"""Dependency analysis exceptions module.

Defines the exception hierarchy for dependency relationship analysis in CodeAtlas.
"""


class DependencyError(Exception):
    """Base exception class for all dependency layer domain errors."""

    pass


class DependencyAnalysisError(DependencyError):
    """Raised when building or aggregating dependencies fails."""

    pass
