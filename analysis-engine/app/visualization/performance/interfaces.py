"""Visualization performance cache interfaces module.

Defines the abstract interface for visualization cache strategies.
"""

from abc import ABC, abstractmethod
from typing import Any


class VisualizationCache(ABC):
    """Abstract base class interface for visualization caching strategies."""

    @abstractmethod
    def get(self, key: str) -> Any | None:
        """Retrieves a cached value for the specified key.

        Args:
            key: Deterministic cache key.

        Returns:
            The cached object or None if it is a cache miss.
        """
        pass

    @abstractmethod
    def set(self, key: str, value: Any) -> None:
        """Caches a value under the specified key.

        Args:
            key: Deterministic cache key.
            value: Object to cache.
        """
        pass

    @abstractmethod
    def invalidate(self, key: str) -> None:
        """Invalidates / removes the cache entry associated with the key.

        Args:
            key: Deterministic cache key.
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clears all cached entries and resets statistics where appropriate."""
        pass

    @abstractmethod
    def get_stats(self) -> dict[str, int]:
        """Exposes runtime caching metrics and statistics.

        Returns:
            Dictionary containing cache metrics (hits, misses, size, invalidations).
        """
        pass
