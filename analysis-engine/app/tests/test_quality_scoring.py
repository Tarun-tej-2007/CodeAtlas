"""Unit tests for the QualityScorer component."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.quality_analysis import (
    MetricCategory,
    QualityLevel,
    QualityMetric,
    QualitySummary,
    QualityScorer,
)


class TestQualityScorer(unittest.TestCase):
    """Verifies weighted quality scoring calculations, invalid weight rejections, and thread-safety under parallel score requests."""

    def setUp(self) -> None:
        # Pre-configured metrics for testing
        self.m_maintainability = QualityMetric(
            name="avg-file-size",
            category=MetricCategory.MAINTAINABILITY,
            value=80.0,
            level=QualityLevel.GOOD,
        )
        self.m_complexity = QualityMetric(
            name="complexity",
            category=MetricCategory.COMPLEXITY,
            value=60.0,
            level=QualityLevel.FAIR,
        )
        self.m_coupling = QualityMetric(
            name="coupling",
            category=MetricCategory.COUPLING,
            value=90.0,
            level=QualityLevel.EXCELLENT,
        )

    def test_invalid_weight_configurations(self) -> None:
        """Verifies scorer rejects negative weight configurations."""
        with self.assertRaises(ValueError):
            QualityScorer(category_weights={MetricCategory.COMPLEXITY: -1.5})

    def test_empty_metrics_collection(self) -> None:
        """Verifies score defaults under empty lists."""
        scorer = QualityScorer()
        summary = scorer.score([])

        self.assertEqual(summary.overall_score, 0.0)
        self.assertEqual(summary.overall_level, QualityLevel.CRITICAL)
        self.assertEqual(len(summary.metrics_by_category), 0)

    def test_unweighted_average_scoring(self) -> None:
        """Verifies default unweighted category average scoring calculations."""
        # Setup scorer without category weights (defaults to 1.0 each)
        scorer = QualityScorer()

        # Input: Maintainability (80.0), Complexity (60.0), Coupling (90.0)
        # Average: (80 + 60 + 90) / 3 = 76.666...
        summary = scorer.score([self.m_maintainability, self.m_complexity, self.m_coupling])

        self.assertAlmostEqual(summary.overall_score, 76.6666667)
        self.assertEqual(summary.overall_level, QualityLevel.GOOD)  # 76.66 >= 75.0 is GOOD
        self.assertEqual(
            dict(summary.metrics_by_category),
            {
                MetricCategory.MAINTAINABILITY: 80.0,
                MetricCategory.COMPLEXITY: 60.0,
                MetricCategory.COUPLING: 90.0,
            },
        )

    def test_weighted_scoring_calculation(self) -> None:
        """Verifies weighted category scores are aggregated correctly."""
        # Weighted setup:
        # Maintainability = weight 3.0
        # Complexity = weight 1.0
        # Coupling = weight 0.0 (ignored completely)
        scorer = QualityScorer(
            category_weights={
                MetricCategory.MAINTAINABILITY: 3.0,
                MetricCategory.COMPLEXITY: 1.0,
                MetricCategory.COUPLING: 0.0,
            }
        )

        # Value: Maintainability (80.0), Complexity (60.0)
        # Weighted Overall Score: (80.0 * 3.0 + 60.0 * 1.0) / (3.0 + 1.0)
        #                        = (240.0 + 60.0) / 4.0 = 300.0 / 4.0 = 75.0
        summary = scorer.score([self.m_maintainability, self.m_complexity, self.m_coupling])

        self.assertEqual(summary.overall_score, 75.0)
        self.assertEqual(summary.overall_level, QualityLevel.GOOD)

    def test_category_grouping_averages(self) -> None:
        """Verifies multiple metrics within the same category are averaged before applying weights."""
        scorer = QualityScorer(
            category_weights={
                MetricCategory.MAINTAINABILITY: 2.0,
                MetricCategory.COMPLEXITY: 1.0,
            }
        )

        m_maint2 = QualityMetric(
            name="symbol-density",
            category=MetricCategory.MAINTAINABILITY,
            value=90.0,
            level=QualityLevel.EXCELLENT,
        )

        # Maintainability metrics: 80.0 and 90.0 => average Maintainability = 85.0
        # Complexity metric: 60.0 => average Complexity = 60.0
        # Weighted overall = (85.0 * 2.0 + 60.0 * 1.0) / (2.0 + 1.0)
        #                  = (170.0 + 60.0) / 3.0 = 230.0 / 3.0 = 76.666...
        summary = scorer.score([self.m_maintainability, m_maint2, self.m_complexity])

        self.assertAlmostEqual(summary.overall_score, 76.6666667)
        self.assertEqual(summary.metrics_by_category[MetricCategory.MAINTAINABILITY], 85.0)

    def test_deterministic_execution(self) -> None:
        """Verifies identical inputs return matching QualitySummary DTOs."""
        scorer = QualityScorer()
        metrics = [self.m_maintainability, self.m_complexity]

        r1 = scorer.score(metrics)
        r2 = scorer.score(metrics)

        self.assertEqual(r1.overall_score, r2.overall_score)
        self.assertEqual(r1.overall_level, r2.overall_level)
        self.assertEqual(r1.metrics_by_category, r2.metrics_by_category)

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety under parallel score computations."""
        scorer = QualityScorer(
            category_weights={
                MetricCategory.MAINTAINABILITY: 2.0,
                MetricCategory.COMPLEXITY: 1.0,
            }
        )
        metrics = [self.m_maintainability, self.m_complexity]

        def run_score():
            return scorer.score(metrics)

        # Run concurrently on 8 threads
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_score) for _ in range(25)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r.overall_score, 73.33333333333333)
            self.assertEqual(r.overall_level, QualityLevel.FAIR)


if __name__ == "__main__":
    unittest.main()
