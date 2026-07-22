"""Visualization performance framework package.

Provides caching, profiling, and runtime metric tracking for scalable pipelines.
"""

from app.visualization.performance.cache import (
    InMemoryVisualizationCache,
    generate_graph_cache_key,
)
from app.visualization.performance.exceptions import (
    CacheError,
    ProfilerError,
    VisualizationPerformanceError,
)
from app.visualization.performance.interfaces import VisualizationCache
from app.visualization.performance.metrics import VisualizationMetrics
from app.visualization.performance.profiler import VisualizationProfiler

__all__ = [
    # Cache
    "VisualizationCache",
    "InMemoryVisualizationCache",
    "generate_graph_cache_key",
    # Profiler
    "VisualizationProfiler",
    # Metrics
    "VisualizationMetrics",
    # Exceptions
    "VisualizationPerformanceError",
    "CacheError",
    "ProfilerError",
]
