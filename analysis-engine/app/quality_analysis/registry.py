"""Quality Metric Registry Module."""

import threading
from typing import Dict, Tuple

from app.quality_analysis.exceptions import QualityMetricError
from app.quality_analysis.metric import QualityMetricEvaluator


class QualityMetricRegistry:
    """Thread-safe, instance-scoped registry for managing and ordering QualityMetricEvaluators."""

    def __init__(self) -> None:
        """Initializes the registry with a thread lock and empty lookup storage."""
        self._lock = threading.Lock()
        self._evaluators: Dict[str, QualityMetricEvaluator] = {}

    def register(self, evaluator: QualityMetricEvaluator) -> None:
        """Registers a new evaluator.

        Raises QualityMetricError if an evaluator with the same name already exists.
        """
        if evaluator is None:
            raise QualityMetricError("Cannot register None evaluator.")
        if not hasattr(evaluator, "metric_name") or not evaluator.metric_name:
            raise QualityMetricError("Evaluator must possess a non-empty 'metric_name'.")

        with self._lock:
            name = evaluator.metric_name
            if name in self._evaluators:
                raise QualityMetricError(f"Quality metric '{name}' is already registered.")
            self._evaluators[name] = evaluator

    def remove(self, name: str) -> None:
        """Removes a registered evaluator by name.

        Raises QualityMetricError if the evaluator is not found.
        """
        with self._lock:
            if name not in self._evaluators:
                raise QualityMetricError(f"Quality metric '{name}' is not registered.")
            del self._evaluators[name]

    def get(self, name: str) -> QualityMetricEvaluator:
        """Retrieves a registered evaluator by name.

        Raises QualityMetricError if the evaluator is not found.
        """
        with self._lock:
            evaluator = self._evaluators.get(name)
            if evaluator is None:
                raise QualityMetricError(f"Quality metric '{name}' is not registered.")
            return evaluator

    def contains(self, name: str) -> bool:
        """Checks if an evaluator is registered under the given name."""
        with self._lock:
            return name in self._evaluators

    def clear(self) -> None:
        """Clears all evaluators from the registry."""
        with self._lock:
            self._evaluators.clear()

    def list_metrics(self) -> Tuple[QualityMetricEvaluator, ...]:
        """Returns all registered evaluators, preserving their deterministic insertion order."""
        with self._lock:
            return tuple(self._evaluators.values())

    def __len__(self) -> int:
        """Returns the number of registered evaluators."""
        with self._lock:
            return len(self._evaluators)
