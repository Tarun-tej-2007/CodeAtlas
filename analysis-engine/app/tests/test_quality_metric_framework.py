"""Unit tests for the Quality Metric Framework layer."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.quality_analysis import (
    MetricCategory,
    QualityLevel,
    QualityMetric,
    QualityMetricError,
    QualityMetricEvaluator,
    QualityMetricRegistry,
)


class MockMetricEvaluator(QualityMetricEvaluator):
    """Mock implementation of QualityMetricEvaluator for testing registry behaviors."""

    def __init__(self, name: str, category: MetricCategory) -> None:
        self._name = name
        self._category = category

    @property
    def metric_name(self) -> str:
        return self._name

    @property
    def category(self) -> MetricCategory:
        return self._category

    @property
    def description(self) -> str:
        return f"Mock evaluator for {self._name}"

    def evaluate(self, context: Any, *args, **kwargs) -> QualityMetric:
        # Dummy evaluation returning a static value
        return QualityMetric(
            name=self._name,
            category=self._category,
            value=85.0,
            level=QualityLevel.GOOD,
            description=self.description,
        )


class TestQualityMetricFramework(unittest.TestCase):
    """Verifies registry lookups, duplication protections, isolation, and thread safety under concurrent writes."""

    def setUp(self) -> None:
        self.registry = QualityMetricRegistry()
        self.eval1 = MockMetricEvaluator("metric-1", MetricCategory.MAINTAINABILITY)
        self.eval2 = MockMetricEvaluator("metric-2", MetricCategory.COUPLING)

    def test_evaluator_interface_properties(self) -> None:
        """Verifies abstract interface cannot be instantiated and mock evaluator acts correctly."""
        with self.assertRaises(TypeError):
            QualityMetricEvaluator()  # type: ignore

        self.assertEqual(self.eval1.metric_name, "metric-1")
        self.assertEqual(self.eval1.category, MetricCategory.MAINTAINABILITY)
        self.assertEqual(self.eval1.description, "Mock evaluator for metric-1")

        # Assert evaluate output DTO
        metric_dto = self.eval1.evaluate(None)
        self.assertEqual(metric_dto.name, "metric-1")
        self.assertEqual(metric_dto.value, 85.0)

    def test_registration_and_lookup_and_contains(self) -> None:
        """Verifies successful registration, contains check, and retrieval."""
        self.assertFalse(self.registry.contains("metric-1"))
        self.assertEqual(len(self.registry), 0)

        # Act
        self.registry.register(self.eval1)

        # Assert
        self.assertTrue(self.registry.contains("metric-1"))
        self.assertEqual(len(self.registry), 1)
        self.assertEqual(self.registry.get("metric-1"), self.eval1)

    def test_duplicate_registration_rejection(self) -> None:
        """Verifies registry raises QualityMetricError on duplicate name registrations."""
        self.registry.register(self.eval1)

        duplicate = MockMetricEvaluator("metric-1", MetricCategory.COMPLEXITY)
        with self.assertRaises(QualityMetricError):
            self.registry.register(duplicate)

    def test_removal_and_clear(self) -> None:
        """Verifies evaluator deletion and total clear functions."""
        self.registry.register(self.eval1)
        self.registry.register(self.eval2)
        self.assertEqual(len(self.registry), 2)

        # Remove single
        self.registry.remove("metric-1")
        self.assertFalse(self.registry.contains("metric-1"))
        self.assertEqual(len(self.registry), 1)

        # Fail remove missing
        with self.assertRaises(QualityMetricError):
            self.registry.remove("metric-1")

        # Clear remaining
        self.registry.clear()
        self.assertEqual(len(self.registry), 0)
        self.assertFalse(self.registry.contains("metric-2"))

    def test_deterministic_ordering(self) -> None:
        """Verifies list preserves exact insertion order."""
        self.registry.register(self.eval2)
        self.registry.register(self.eval1)

        metrics = self.registry.list_metrics()
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0], self.eval2)
        self.assertEqual(metrics[1], self.eval1)

    def test_registry_isolation(self) -> None:
        """Verifies separate registry instances maintain distinct state boundaries."""
        registry2 = QualityMetricRegistry()
        self.registry.register(self.eval1)

        self.assertTrue(self.registry.contains("metric-1"))
        self.assertFalse(registry2.contains("metric-1"))

    def test_concurrent_registration_and_lookup(self) -> None:
        """Verifies thread-safety under simultaneous registry writes and reads."""
        def run_concurrency(index: int) -> None:
            # Register a distinct evaluator
            evaluator = MockMetricEvaluator(f"concurrent-{index}", MetricCategory.TESTABILITY)
            self.registry.register(evaluator)

            # Concurrent reads and contains checks
            _ = self.registry.contains(f"concurrent-{index}")
            _ = self.registry.get(f"concurrent-{index}")
            _ = self.registry.list_metrics()

        # Execute concurrently across 8 threads
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_concurrency, idx) for idx in range(30)]
            # Ensure no threads raised exceptions
            for f in futures:
                f.result()

        self.assertEqual(len(self.registry), 30)


if __name__ == "__main__":
    unittest.main()
