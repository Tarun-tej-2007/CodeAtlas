"""Unit tests for the Complexity Metrics Evaluator."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.quality_analysis import (
    MetricCategory,
    QualityLevel,
    QualityMetricRegistry,
    AverageNestingDepthEvaluator,
)


class MockScope:
    """Mock semantic scope structure."""

    def __init__(self, scope_id: str, parent_id: str | None = None) -> None:
        self.id = scope_id
        self.parent_scope_id = parent_id


class MockSemanticResult:
    """Mock semantic result containing scopes."""

    def __init__(self, scopes: list[MockScope]) -> None:
        self.scopes = scopes


class TestComplexityMetrics(unittest.TestCase):
    """Verifies nesting depth calculations, threshold evaluations, registries compatibility, and concurrency."""

    def setUp(self) -> None:
        self.registry = QualityMetricRegistry()
        self.depth_eval = AverageNestingDepthEvaluator(
            good_threshold_depth=1.5,
            fair_threshold_depth=3.0,
            poor_threshold_depth=4.5,
            metric_id="test-nesting-depth",
        )

    def test_invalid_constructor_parameters(self) -> None:
        """Verifies threshold bounds validation controls."""
        with self.assertRaises(ValueError):
            AverageNestingDepthEvaluator(good_threshold_depth=-1.0)

        with self.assertRaises(ValueError):
            AverageNestingDepthEvaluator(
                good_threshold_depth=3.0,
                fair_threshold_depth=2.0,
                poor_threshold_depth=5.0,
            )

    def test_average_nesting_depth_calculation(self) -> None:
        """Verifies average lexical nesting depth values and levels."""
        # 1. EXCELLENT: 2 scopes. S1 (root, depth 0), S2 (child of S1, depth 1)
        # Average: (0 + 1) / 2 = 0.5 <= 1.5
        scopes_exc = [MockScope("S1"), MockScope("S2", "S1")]
        ctx_exc = MockSemanticResult(scopes_exc)
        m1 = self.depth_eval.evaluate(ctx_exc)
        self.assertEqual(m1.value, 0.5)
        self.assertEqual(m1.level, QualityLevel.EXCELLENT)

        # 2. GOOD: S1 (0), S2 (child of S1, 1), S3 (child of S2, 2)
        # Average: (0 + 1 + 2) / 3 = 1.0 <= 1.5 (still EXCELLENT since avg <= 1.5)
        # Let's design S1 (0), S2 (1), S3 (2), S4 (3)
        # Average: (0 + 1 + 2 + 3) / 4 = 1.5 <= 1.5 => EXCELLENT
        # S1 (0), S2 (1), S3 (2), S4 (3), S5 (4)
        # Average: (0+1+2+3+4)/5 = 2.0 <= 3.0 => GOOD
        scopes_good = [
            MockScope("S1"),
            MockScope("S2", "S1"),
            MockScope("S3", "S2"),
            MockScope("S4", "S3"),
            MockScope("S5", "S4"),
        ]
        ctx_good = MockSemanticResult(scopes_good)
        m2 = self.depth_eval.evaluate(ctx_good)
        self.assertEqual(m2.value, 2.0)
        self.assertEqual(m2.level, QualityLevel.GOOD)

        # 3. POOR: S1(0), S2(1), S3(2), S4(3), S5(4), S6(5), S7(6)
        # Average: (0+1+2+3+4+5+6)/7 = 21 / 7 = 3.0 <= 3.0 => GOOD (actually GOOD/FAIR boundary)
        # Let's construct a deeper hierarchy
        # S1(0), S2(1), S3(2), S4(3), S5(4), S6(5), S7(6), S8(7), S9(8), S10(9)
        # Average: 45 / 10 = 4.5 <= 4.5 => FAIR (boundary)
        # 11 scopes: avg = 55 / 11 = 5.0 > 4.5 => POOR
        scopes_poor = [MockScope("S1")]
        for idx in range(2, 12):
            scopes_poor.append(MockScope(f"S{idx}", f"S{idx-1}"))
        ctx_poor = MockSemanticResult(scopes_poor)
        m3 = self.depth_eval.evaluate(ctx_poor)
        self.assertEqual(m3.value, 5.0)
        self.assertEqual(m3.level, QualityLevel.POOR)

    def test_cycle_detection(self) -> None:
        """Verifies cycle loop protection under recursive nesting trees."""
        # Setup S1 -> S2 -> S1
        scopes_cycle = [MockScope("S1", "S2"), MockScope("S2", "S1")]
        ctx = MockSemanticResult(scopes_cycle)
        m = self.depth_eval.evaluate(ctx)
        # S1 parent is S2 (depth = S2_depth + 1 = 1 + 1 = 2)
        # Cycle breaks safely; depth evaluations remain bounded
        self.assertLessEqual(m.value, 2.0)

    def test_empty_contexts(self) -> None:
        """Verifies default results under empty scopes."""
        ctx_empty = MockSemanticResult([])
        m = self.depth_eval.evaluate(ctx_empty)
        self.assertEqual(m.value, 0.0)
        self.assertEqual(m.level, QualityLevel.EXCELLENT)

    def test_registry_compatibility(self) -> None:
        """Verifies evaluator registers cleanly with the registry."""
        self.registry.register(self.depth_eval)
        self.assertEqual(len(self.registry), 1)
        self.assertEqual(self.registry.get("test-nesting-depth"), self.depth_eval)

    def test_deterministic_execution(self) -> None:
        """Verifies identical inputs return matching metric DTOs."""
        scopes = [MockScope("S1"), MockScope("S2", "S1")]
        ctx = MockSemanticResult(scopes)
        r1 = self.depth_eval.evaluate(ctx)
        r2 = self.depth_eval.evaluate(ctx)
        self.assertEqual(r1, r2)

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safe execution under parallel invocations."""
        scopes = [MockScope("S1"), MockScope("S2", "S1")]
        ctx = MockSemanticResult(scopes)

        def run_evaluate():
            return self.depth_eval.evaluate(ctx)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_evaluate) for _ in range(20)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r.value, 0.5)
            self.assertEqual(r.level, QualityLevel.EXCELLENT)


if __name__ == "__main__":
    unittest.main()
