"""Visualization performance cache implementations module.

Provides InMemoryVisualizationCache and deterministic cache key generation.
"""

import hashlib
import json
from typing import Any
from app.graph import Graph as RepositoryGraph
from app.visualization.performance.interfaces import VisualizationCache
from app.visualization.performance.exceptions import CacheError


def generate_graph_cache_key(graph: RepositoryGraph) -> str:
    """Generates a stable, deterministic cache key from a RepositoryGraph's logical state.

    Args:
        graph: RepositoryGraph instance.

    Returns:
        Hexadecimal SHA-256 string representing the graph state.

    Raises:
        CacheError: If the graph structure is invalid or serialization fails.
    """
    try:
        if graph is None:
            raise CacheError("Cannot generate cache key for None graph.")

        # Sort nodes and edges by ID to enforce deterministic layout structure
        sorted_nodes = sorted(graph.nodes, key=lambda n: n.id)
        sorted_edges = sorted(graph.edges, key=lambda e: e.id)

        state_dict = {
            "project_name": graph.metadata.project_name,
            "nodes": [
                {
                    "id": n.id,
                    "type": n.type.value if hasattr(n.type, "value") else str(n.type),
                    "name": n.name,
                    "path": str(n.path) if n.path else None,
                    "line": n.line,
                    "metadata": sorted(n.metadata.items()) if n.metadata else [],
                }
                for n in sorted_nodes
            ],
            "edges": [
                {
                    "id": e.id,
                    "source": e.source,
                    "target": e.target,
                    "type": e.type.value if hasattr(e.type, "value") else str(e.type),
                    "metadata": sorted(e.metadata.items()) if e.metadata else [],
                }
                for e in sorted_edges
            ],
        }

        # JSON dump with sorted keys guarantees deterministic output across runs
        serialized = json.dumps(state_dict, sort_keys=True)
        return hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    except Exception as err:
        raise CacheError(f"Failed to generate graph cache key: {err}") from err


class InMemoryVisualizationCache(VisualizationCache):
    """In-memory cache implementation mapping deterministic keys to visualization payloads."""

    def __init__(self) -> None:
        """Initializes InMemoryVisualizationCache and resets statistics."""
        self._cache: dict[str, Any] = {}
        self._hits = 0
        self._misses = 0
        self._invalidations = 0

    def get(self, key: str) -> Any | None:
        """Retrieves a cached value for the key."""
        if key in self._cache:
            self._hits += 1
            return self._cache[key]
        self._misses += 1
        return None

    def set(self, key: str, value: Any) -> None:
        """Caches a value under the key."""
        self._cache[key] = value

    def invalidate(self, key: str) -> None:
        """Invalidates/removes the cache entry associated with the key."""
        if key in self._cache:
            del self._cache[key]
            self._invalidations += 1

    def clear(self) -> None:
        """Clears all cached entries and resets stats."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
        self._invalidations = 0

    def get_stats(self) -> dict[str, int]:
        """Exposes runtime caching metrics and statistics."""
        return {
            "hits": self._hits,
            "misses": self._misses,
            "invalidations": self._invalidations,
            "size": len(self._cache),
        }
