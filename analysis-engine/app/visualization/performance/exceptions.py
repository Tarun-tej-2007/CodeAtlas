"""Visualization performance exceptions module.

Defines exceptions raised by the caching, profiling, and metrics collection layers.
"""

from app.visualization.exceptions import VisualizationError


class VisualizationPerformanceError(VisualizationError):
    """Base exception class for all visualization performance framework errors."""

    pass


class CacheError(VisualizationPerformanceError):
    """Raised when a cache access, validation, or invalidation failure occurs."""

    pass


class ProfilerError(VisualizationPerformanceError):
    """Raised when profiling execution timing collection fails."""

    pass
