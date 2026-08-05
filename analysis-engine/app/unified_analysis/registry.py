"""Unified Analysis Registry Module."""

import threading
from typing import Dict, Tuple

from app.unified_analysis.contributor import UnifiedAnalysisContributor
from app.unified_analysis.exceptions import UnifiedAnalysisAggregationError


class UnifiedAnalysisRegistry:
    """Thread-safe, insertion-order preserving registry for managing UnifiedAnalysisContributors."""

    def __init__(self) -> None:
        """Initializes the registry with a thread lock and empty contributor storage."""
        self._lock = threading.Lock()
        self._contributors: Dict[str, UnifiedAnalysisContributor] = {}

    def register(self, contributor: UnifiedAnalysisContributor) -> None:
        """Registers a new UnifiedAnalysisContributor.

        Raises UnifiedAnalysisAggregationError on duplicate or invalid registrations.
        """
        if contributor is None:
            raise UnifiedAnalysisAggregationError("Cannot register None contributor.")
        if not isinstance(contributor, UnifiedAnalysisContributor):
            raise UnifiedAnalysisAggregationError(
                "Registered object must inherit from UnifiedAnalysisContributor."
            )
        name = contributor.contributor_name
        if not name or not name.strip():
            raise UnifiedAnalysisAggregationError("Contributor must possess a non-empty name.")

        with self._lock:
            if name in self._contributors:
                raise UnifiedAnalysisAggregationError(
                    f"Contributor '{name}' is already registered."
                )
            self._contributors[name] = contributor

    def unregister(self, name: str) -> None:
        """Removes a registered contributor by name.

        Raises UnifiedAnalysisAggregationError if not found.
        """
        if not name:
            raise UnifiedAnalysisAggregationError("Contributor name must not be empty.")

        with self._lock:
            if name not in self._contributors:
                raise UnifiedAnalysisAggregationError(
                    f"Contributor '{name}' is not registered."
                )
            del self._contributors[name]

    def get(self, name: str) -> UnifiedAnalysisContributor:
        """Retrieves a registered contributor by name.

        Raises UnifiedAnalysisAggregationError if not found.
        """
        if not name:
            raise UnifiedAnalysisAggregationError("Contributor name must not be empty.")

        with self._lock:
            contributor = self._contributors.get(name)
            if contributor is None:
                raise UnifiedAnalysisAggregationError(
                    f"Contributor '{name}' is not registered."
                )
            return contributor

    def contains(self, name: str) -> bool:
        """Checks if a contributor is registered under the given name."""
        if not name:
            return False

        with self._lock:
            return name in self._contributors

    def list_contributors(self) -> Tuple[UnifiedAnalysisContributor, ...]:
        """Returns all registered contributors, preserving their deterministic insertion order."""
        with self._lock:
            return tuple(self._contributors.values())

    def clear(self) -> None:
        """Clears all contributors from the registry."""
        with self._lock:
            self._contributors.clear()

    def __len__(self) -> int:
        """Returns the number of registered contributors."""
        with self._lock:
            return len(self._contributors)
