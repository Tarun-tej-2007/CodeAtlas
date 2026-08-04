"""Unit tests for the Maintainability Metrics Evaluators."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.quality_analysis import (
    MetricCategory,
    QualityLevel,
    QualityMetricRegistry,
    AverageFileSizeEvaluator,
    SymbolDensityEvaluator,
)


class MockFile:
    """Mock file representation containing size."""

    def __init__(self, size: int) -> None:
        self.size = size


class MockProjectFile:
    """Mock project file containing list of symbols."""

    def __init__(self, symbol_count: int) -> None:
        self.symbols = [object() for _ in range(symbol_count)]


class MockScanResult:
    """Mock ScanResult wrapping files list."""

    def __init__(self, sizes: list[int]) -> None:
        self.files = [MockFile(s) for s in sizes]


class MockProjectSemanticResult:
    """Mock ProjectSemanticResult wrapping dict of ProjectFiles."""

    def __init__(self, symbol_counts: dict[Path, int]) -> None:
        self.files = {path: MockProjectFile(cnt) for path, cnt in symbol_counts.items()}


class TestMaintainabilityMetrics(unittest.TestCase):
    """Verifies metric computations, levels matching thresholds, registry validations, and concurrency."""

    def setUp(self) -> None:
        self.registry = QualityMetricRegistry()

        # Instantiate evaluators with custom thresholds
        self.size_eval = AverageFileSizeEvaluator(
            good_threshold_bytes=1000,
            fair_threshold_bytes=5000,
            poor_threshold_bytes=10000,
            metric_id="test-file-size",
        )
        self.density_eval = SymbolDensityEvaluator(
            good_threshold_density=10.0,
            fair_threshold_density=20.0,
            poor_threshold_density=30.0,
            metric_id="test-symbol-density",
        )

    def test_invalid_constructor_parameters(self) -> None:
        """Verifies threshold inputs are validated in constructor."""
        # 1. Non-positive thresholds
        with self.assertRaises(ValueError):
            AverageFileSizeEvaluator(good_threshold_bytes=-100)

        # 2. Out of order thresholds
        with self.assertRaises(ValueError):
            SymbolDensityEvaluator(
                good_threshold_density=15.0,
                fair_threshold_density=10.0,
                poor_threshold_density=30.0,
            )

    def test_average_file_size_evaluation(self) -> None:
        """Verifies average file size metric values and levels."""
        # Setup context matching different quality levels
        # Thresholds: 1000, 5000, 10000

        # EXCELLENT: average 500 <= 1000
        ctx_excellent = MockScanResult([400, 600])
        metric_exc = self.size_eval.evaluate(ctx_excellent)
        self.assertEqual(metric_exc.value, 500.0)
        self.assertEqual(metric_exc.level, QualityLevel.EXCELLENT)

        # GOOD: average 3000 <= 5000
        ctx_good = MockScanResult([2000, 4000])
        metric_good = self.size_eval.evaluate(ctx_good)
        self.assertEqual(metric_good.level, QualityLevel.GOOD)

        # FAIR: average 8000 <= 10000
        ctx_fair = MockScanResult([6000, 10000])
        metric_fair = self.size_eval.evaluate(ctx_fair)
        self.assertEqual(metric_fair.level, QualityLevel.FAIR)

        # POOR: average 15000 > 10000
        ctx_poor = MockScanResult([12000, 18000])
        metric_poor = self.size_eval.evaluate(ctx_poor)
        self.assertEqual(metric_poor.level, QualityLevel.POOR)

    def test_symbol_density_evaluation(self) -> None:
        """Verifies average symbol density metric values and levels."""
        # Thresholds: 10.0, 20.0, 30.0

        # EXCELLENT: average 5.0 <= 10.0
        ctx_excellent = MockProjectSemanticResult(
            {Path("a.py"): 4, Path("b.py"): 6}
        )
        metric_exc = self.density_eval.evaluate(ctx_excellent)
        self.assertEqual(metric_exc.value, 5.0)
        self.assertEqual(metric_exc.level, QualityLevel.EXCELLENT)

        # POOR: average 40.0 > 30.0
        ctx_poor = MockProjectSemanticResult(
            {Path("a.py"): 35, Path("b.py"): 45}
        )
        metric_poor = self.density_eval.evaluate(ctx_poor)
        self.assertEqual(metric_poor.level, QualityLevel.POOR)

    def test_empty_inputs_handling(self) -> None:
        """Verifies correct execution defaults when scan or semantic results contain no files."""
        empty_scan = MockScanResult([])
        metric_size = self.size_eval.evaluate(empty_scan)
        self.assertEqual(metric_size.value, 0.0)
        self.assertEqual(metric_size.level, QualityLevel.EXCELLENT)

        empty_sem = MockProjectSemanticResult({})
        metric_dens = self.density_eval.evaluate(empty_sem)
        self.assertEqual(metric_dens.value, 0.0)
        self.assertEqual(metric_dens.level, QualityLevel.EXCELLENT)

    def test_registry_compatibility(self) -> None:
        """Verifies that evaluators register cleanly into QualityMetricRegistry."""
        self.registry.register(self.size_eval)
        self.registry.register(self.density_eval)

        self.assertEqual(len(self.registry), 2)
        self.assertEqual(self.registry.get("test-file-size"), self.size_eval)
        self.assertEqual(self.registry.get("test-symbol-density"), self.density_eval)

    def test_deterministic_output(self) -> None:
        """Verifies duplicate runs return identical metrics output DTOs."""
        ctx = MockScanResult([500, 1500])
        r1 = self.size_eval.evaluate(ctx)
        r2 = self.size_eval.evaluate(ctx)
        self.assertEqual(r1, r2)

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safe execution of metric calculations."""
        ctx = MockScanResult([400, 600, 800])

        def run_evaluate():
            return self.size_eval.evaluate(ctx)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_evaluate) for _ in range(25)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r.value, 600.0)
            self.assertEqual(r.level, QualityLevel.EXCELLENT)


if __name__ == "__main__":
    unittest.main()
