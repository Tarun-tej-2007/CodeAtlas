"""Unit tests for the QualityEvaluationEngine component."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any

from app.quality_analysis import (
    MetricCategory,
    QualityLevel,
    QualityMetric,
    QualityMetricRegistry,
    QualityReport,
    QualityEvaluationEngine,
)
from app.quality_analysis.metric import QualityMetricEvaluator


class MockEvaluator(QualityMetricEvaluator):
    """Mock evaluator implementation to inspect context forwarding and registration order execution."""

    def __init__(self, name: str, category: MetricCategory, score: float) -> None:
        self._name = name
        self._category = category
        self._score = score
        self.invoked_with = []

    @property
    def metric_name(self) -> str:
        return self._name

    @property
    def category(self) -> MetricCategory:
        return self._category

    @property
    def description(self) -> str:
        return f"Mock {self._name}"

    def evaluate(self, context: Any, *args, **kwargs) -> QualityMetric:
        # Trace parameter context forwarding
        self.invoked_with.append((context, kwargs))
        return QualityMetric(
            name=self._name,
            category=self._category,
            value=self._score,
            level=QualityLevel.GOOD,
            description=self.description,
        )


class FailingEvaluator(QualityMetricEvaluator):
    """Mock evaluator that raises an exception during execution."""

    @property
    def metric_name(self) -> str:
        return "failing-metric"

    @property
    def category(self) -> MetricCategory:
        return MetricCategory.MAINTAINABILITY

    @property
    def description(self) -> str:
        return "Always fails"

    def evaluate(self, context: Any, *args, **kwargs) -> QualityMetric:
        raise ValueError("Intentional evaluator crash")


class TestQualityEvaluationEngine(unittest.TestCase):
    """Verifies sequence orchestration, order, averages, exception propagation, and thread safety."""

    def setUp(self) -> None:
        self.registry = QualityMetricRegistry()
        self.engine = QualityEvaluationEngine(self.registry)

        self.eval1 = MockEvaluator("metric-1", MetricCategory.MAINTAINABILITY, 80.0)
        self.eval2 = MockEvaluator("metric-2", MetricCategory.COUPLING, 90.0)
        self.eval3 = MockEvaluator("metric-3", MetricCategory.MAINTAINABILITY, 70.0)

    def test_constructor_validation(self) -> None:
        """Verifies engine init assertion limits."""
        with self.assertRaises(ValueError):
            QualityEvaluationEngine(None)  # type: ignore

    def test_empty_registry_execution(self) -> None:
        """Verifies report defaults when zero metrics are registered."""
        report = self.engine.analyze(project_name="EmptyProj", context="OpaqueCtx")

        self.assertEqual(report.project_name, "EmptyProj")
        self.assertEqual(len(report.metrics), 0)
        self.assertEqual(report.summary.overall_score, 0.0)
        self.assertEqual(report.summary.overall_level, QualityLevel.CRITICAL)
        self.assertEqual(len(report.summary.metrics_by_category), 0)

        # Confirm timezone-aware UTC datetime format
        self.assertIsNotNone(report.generated_at.tzinfo)
        self.assertEqual(report.generated_at.tzinfo, timezone.utc)

    def test_single_evaluator_execution(self) -> None:
        """Verifies mapping structures for one metric evaluator."""
        self.registry.register(self.eval1)

        report = self.engine.analyze(project_name="SingleProj", context="Ctx")

        self.assertEqual(len(report.metrics), 1)
        self.assertEqual(report.metrics[0].name, "metric-1")
        self.assertEqual(report.summary.overall_score, 80.0)
        self.assertEqual(report.summary.overall_level, QualityLevel.GOOD)
        self.assertEqual(
            dict(report.summary.metrics_by_category), {MetricCategory.MAINTAINABILITY: 80.0}
        )

    def test_multiple_evaluators_averages_and_ordering(self) -> None:
        """Verifies execution ordering and aggregated category segmented averages."""
        # Register in specific sequence
        self.registry.register(self.eval2)  # COUPLING (90.0)
        self.registry.register(self.eval1)  # MAINTAINABILITY (80.0)
        self.registry.register(self.eval3)  # MAINTAINABILITY (70.0)

        report = self.engine.analyze(project_name="MultiProj", context="MyContext", extra_arg="ok")

        # Assert registration-order preservation
        self.assertEqual(len(report.metrics), 3)
        self.assertEqual(report.metrics[0].name, "metric-2")
        self.assertEqual(report.metrics[1].name, "metric-1")
        self.assertEqual(report.metrics[2].name, "metric-3")

        # Category segment average assertions
        # MAINTAINABILITY = (80 + 70) / 2 = 75.0
        # COUPLING = 90.0
        expected_categories = {
            MetricCategory.COUPLING: 90.0,
            MetricCategory.MAINTAINABILITY: 75.0,
        }
        self.assertEqual(dict(report.summary.metrics_by_category), expected_categories)

        # Overall average = (90 + 80 + 70) / 3 = 80.0
        self.assertEqual(report.summary.overall_score, 80.0)
        self.assertEqual(report.summary.overall_level, QualityLevel.GOOD)

    def test_context_and_arguments_forwarding(self) -> None:
        """Verifies parameter forwarding to evaluators."""
        self.registry.register(self.eval1)

        self.engine.analyze(project_name="ForwardProj", context="SharedCtx", custom_val=42)

        self.assertEqual(len(self.eval1.invoked_with), 1)
        ctx, kwargs = self.eval1.invoked_with[0]
        self.assertEqual(ctx, "SharedCtx")
        self.assertEqual(kwargs, {"custom_val": 42})

    def test_exception_propagation(self) -> None:
        """Verifies evaluator crash propagates cleanly without wrapping."""
        self.registry.register(self.eval1)
        self.registry.register(FailingEvaluator())

        with self.assertRaises(ValueError) as ctx:
            self.engine.analyze(project_name="FailProj", context="Ctx")

        self.assertEqual(str(ctx.exception), "Intentional evaluator crash")

    def test_deterministic_output(self) -> None:
        """Verifies identical inputs produce equivalent summary and reports."""
        self.registry.register(self.eval1)
        self.registry.register(self.eval2)

        r1 = self.engine.analyze(project_name="DetProj", context="Ctx")
        r2 = self.engine.analyze(project_name="DetProj", context="Ctx")

        self.assertEqual(r1.project_name, r2.project_name)
        self.assertEqual(r1.summary, r2.summary)
        self.assertEqual(len(r1.metrics), len(r2.metrics))
        for m1, m2 in zip(r1.metrics, r2.metrics):
            self.assertEqual(m1, m2)

    def test_registry_isolation(self) -> None:
        """Verifies separate engine instances with separate registries do not bleed state."""
        reg2 = QualityMetricRegistry()
        engine2 = QualityEvaluationEngine(reg2)

        self.registry.register(self.eval1)
        reg2.register(self.eval2)

        rep1 = self.engine.analyze(project_name="Proj1", context="Ctx")
        rep2 = engine2.analyze(project_name="Proj2", context="Ctx")

        self.assertEqual(len(rep1.metrics), 1)
        self.assertEqual(rep1.metrics[0].name, "metric-1")

        self.assertEqual(len(rep2.metrics), 1)
        self.assertEqual(rep2.metrics[0].name, "metric-2")

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safe stateless execution under parallel analyze runs."""
        self.registry.register(self.eval1)
        self.registry.register(self.eval2)

        def run_analyze():
            return self.engine.analyze(project_name="ConcurrentProj", context="Ctx")

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analyze) for _ in range(20)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r.summary.overall_score, 85.0)
            self.assertEqual(r.summary.overall_level, QualityLevel.GOOD)


if __name__ == "__main__":
    unittest.main()
