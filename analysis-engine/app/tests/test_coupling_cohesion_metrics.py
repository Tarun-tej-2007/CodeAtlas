"""Unit tests for the Coupling and Cohesion Metrics Evaluators."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.quality_analysis import (
    MetricCategory,
    QualityLevel,
    QualityMetricRegistry,
    AverageCouplingEvaluator,
    AverageCohesionEvaluator,
)


class MockGraphNode:
    def __init__(self, node_id: str) -> None:
        self.id = node_id


class MockGraphEdge:
    def __init__(self, source: str, target: str) -> None:
        self.source_id = source
        self.target_id = target


class MockDependencyGraph:
    """Mock DependencyGraph DTO structure."""

    def __init__(self, nodes: list[str], edges: list[tuple[str, str]]) -> None:
        self.nodes = [MockGraphNode(n) for n in nodes]
        self.edges = [MockGraphEdge(s, t) for s, t in edges]


class MockLocation:
    """Mock location coordinate."""

    def __init__(self, path: Path) -> None:
        self.file_path = path


class MockSymbolReference:
    """Mock symbol usage reference."""

    def __init__(self, file_path: Path) -> None:
        self.location = MockLocation(file_path)


class MockProjectSymbol:
    """Mock project symbol definition."""

    def __init__(self, file_path: Path) -> None:
        self.location = MockLocation(file_path)


class MockResolvedReference:
    """Mock cross-file resolved reference mapping."""

    def __init__(self, ref_path: Path, target_path: Path) -> None:
        self.reference = MockSymbolReference(ref_path)
        self.target_symbol = MockProjectSymbol(target_path)


class MockReferenceResolutionResult:
    """Mock reference resolution result."""

    def __init__(self, resolved: list[MockResolvedReference]) -> None:
        self.resolved_references = resolved


class TestCouplingCohesionMetrics(unittest.TestCase):
    """Verifies coupling calculations, cohesion internal ratios, thresholds logic, registry wiring, and concurrency."""

    def setUp(self) -> None:
        self.registry = QualityMetricRegistry()

        # Configurable constructors
        self.coupling_eval = AverageCouplingEvaluator(
            good_threshold_coupling=1.5,
            fair_threshold_coupling=3.0,
            poor_threshold_coupling=5.0,
            metric_id="test-coupling",
        )
        self.cohesion_eval = AverageCohesionEvaluator(
            good_threshold_cohesion=75.0,
            fair_threshold_cohesion=50.0,
            poor_threshold_cohesion=25.0,
            metric_id="test-cohesion",
        )

    def test_invalid_constructor_parameters(self) -> None:
        """Verifies threshold inputs validation controls."""
        # Coupling out of order
        with self.assertRaises(ValueError):
            AverageCouplingEvaluator(
                good_threshold_coupling=5.0,
                fair_threshold_coupling=2.0,
                poor_threshold_coupling=6.0,
            )

        # Cohesion out of bounds / order
        with self.assertRaises(ValueError):
            AverageCohesionEvaluator(
                good_threshold_cohesion=120.0,  # exceeds 100.0 limit
                fair_threshold_cohesion=50.0,
                poor_threshold_cohesion=30.0,
            )

    def test_average_coupling_evaluation(self) -> None:
        """Verifies average directed coupling connections per node calculation."""
        # 1. EXCELLENT: 2 nodes, 2 edges => avg 1.0 <= 1.5
        g1 = MockDependencyGraph(nodes=["A", "B"], edges=[("A", "B"), ("B", "A")])
        m1 = self.coupling_eval.evaluate(g1)
        self.assertEqual(m1.value, 1.0)
        self.assertEqual(m1.level, QualityLevel.EXCELLENT)

        # 2. GOOD: 2 nodes, 4 edges => avg 2.0 <= 3.0
        g2 = MockDependencyGraph(
            nodes=["A", "B"],
            edges=[("A", "B"), ("B", "A"), ("A", "A"), ("B", "B")],
        )
        m2 = self.coupling_eval.evaluate(g2)
        self.assertEqual(m2.value, 2.0)
        self.assertEqual(m2.level, QualityLevel.GOOD)

        # 3. POOR: 1 node, 6 edges => avg 6.0 > 5.0
        g3 = MockDependencyGraph(
            nodes=["A"],
            edges=[("A", "A")] * 6,
        )
        m3 = self.coupling_eval.evaluate(g3)
        self.assertEqual(m3.level, QualityLevel.POOR)

    def test_average_cohesion_evaluation(self) -> None:
        """Verifies average cohesion ratio calculation from internal vs external references."""
        p_a = Path("a.py")
        p_b = Path("b.py")

        # 1. EXCELLENT: 3 internal resolved, 1 external resolved => 3 / 4 = 75.0% >= 75.0%
        resolved_list = [
            MockResolvedReference(p_a, p_a),
            MockResolvedReference(p_a, p_a),
            MockResolvedReference(p_b, p_b),
            MockResolvedReference(p_a, p_b),  # external
        ]
        ctx = MockReferenceResolutionResult(resolved_list)
        m1 = self.cohesion_eval.evaluate(ctx)
        self.assertEqual(m1.value, 75.0)
        self.assertEqual(m1.level, QualityLevel.EXCELLENT)

        # 2. POOR: 0 internal resolved, 2 external resolved => 0% < 25.0%
        resolved_poor = [
            MockResolvedReference(p_a, p_b),
            MockResolvedReference(p_b, p_a),
        ]
        ctx_poor = MockReferenceResolutionResult(resolved_poor)
        m2 = self.cohesion_eval.evaluate(ctx_poor)
        self.assertEqual(m2.value, 0.0)
        self.assertEqual(m2.level, QualityLevel.POOR)

    def test_empty_contexts(self) -> None:
        """Verifies default results returned under empty graphs or missing references list."""
        g_empty = MockDependencyGraph(nodes=[], edges=[])
        m_coupling = self.coupling_eval.evaluate(g_empty)
        self.assertEqual(m_coupling.value, 0.0)
        self.assertEqual(m_coupling.level, QualityLevel.EXCELLENT)

        ctx_empty = MockReferenceResolutionResult([])
        m_cohesion = self.cohesion_eval.evaluate(ctx_empty)
        self.assertEqual(m_cohesion.value, 100.0)
        self.assertEqual(m_cohesion.level, QualityLevel.EXCELLENT)

    def test_registry_compatibility(self) -> None:
        """Verifies evaluators integrate with QualityMetricRegistry."""
        self.registry.register(self.coupling_eval)
        self.registry.register(self.cohesion_eval)

        self.assertEqual(len(self.registry), 2)
        self.assertEqual(self.registry.get("test-coupling"), self.coupling_eval)
        self.assertEqual(self.registry.get("test-cohesion"), self.cohesion_eval)

    def test_deterministic_execution(self) -> None:
        """Verifies identical inputs produce equivalent quality metrics."""
        g = MockDependencyGraph(nodes=["A", "B"], edges=[("A", "B")])
        r1 = self.coupling_eval.evaluate(g)
        r2 = self.coupling_eval.evaluate(g)
        self.assertEqual(r1, r2)

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safe execution of evaluator formulas."""
        g = MockDependencyGraph(nodes=["A", "B"], edges=[("A", "B")])

        def run_evaluate():
            return self.coupling_eval.evaluate(g)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_evaluate) for _ in range(20)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r.value, 0.5)
            self.assertEqual(r.level, QualityLevel.EXCELLENT)


if __name__ == "__main__":
    unittest.main()
