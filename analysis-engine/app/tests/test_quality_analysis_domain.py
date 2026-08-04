"""Unit tests for the Quality Analysis Domain Foundation layer."""

import unittest
from datetime import datetime, timezone
from pydantic import ValidationError

from app.quality_analysis import (
    MetricCategory,
    QualityLevel,
    QualityAnalysisError,
    QualityMetricError,
    QualityMetric,
    QualitySummary,
    QualityReport,
    QualityAnalyzer,
)


class DummyQualityAnalyzer(QualityAnalyzer):
    """Concrete implementation of QualityAnalyzer interface for testing contract enforcement."""

    def analyze(self, *args, **kwargs) -> QualityReport:
        # Dummy analyzer returns a pre-configured report structure
        summary = QualitySummary(
            overall_score=85.0,
            overall_level=QualityLevel.GOOD,
            metrics_by_category={MetricCategory.MAINTAINABILITY: 85.0},
        )
        return QualityReport(
            project_name="DummyProj",
            generated_at=datetime.now(timezone.utc),
            metrics=(),
            summary=summary,
        )


class TestQualityAnalysisDomain(unittest.TestCase):
    """Verifies DTO models, UTC timestamp rules, metadata read-only blocks, and abstract interfaces."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)

        # Pre-configured DTO structures
        self.metric = QualityMetric(
            name="complexity_metric",
            category=MetricCategory.COMPLEXITY,
            value=12.0,
            level=QualityLevel.GOOD,
            description="Cyclomatic complexity score",
            metadata={"max_limit": 20},
        )
        self.summary = QualitySummary(
            overall_score=90.0,
            overall_level=QualityLevel.EXCELLENT,
            metrics_by_category={MetricCategory.COMPLEXITY: 12.0},
            metadata={"run_version": "v1.2"},
        )
        self.report = QualityReport(
            project_name="TestProject",
            generated_at=self.time_utc,
            metrics=(self.metric,),
            summary=self.summary,
            metadata={"analyzed_branch": "main"},
        )

    def test_enum_validation(self) -> None:
        """Verifies enum categorizations and correct string values."""
        self.assertEqual(MetricCategory.MAINTAINABILITY, "maintainability")
        self.assertEqual(QualityLevel.EXCELLENT, "excellent")

        # Confirm exact count of enums
        self.assertEqual(len(MetricCategory), 8)
        self.assertEqual(len(QualityLevel), 5)

    def test_exception_hierarchy(self) -> None:
        """Verifies custom exceptions inherit from the domain base."""
        self.assertTrue(issubclass(QualityMetricError, QualityAnalysisError))
        self.assertTrue(issubclass(QualityAnalysisError, Exception))

        # Assert raise behaviors
        with self.assertRaises(QualityMetricError):
            raise QualityMetricError("Invalid score value bounds.")

    def test_model_immutability(self) -> None:
        """Verifies that changing fields directly on frozen Pydantic models fails."""
        with self.assertRaises(ValidationError):
            # Attempting to assign value directly raises ValidationError/TypeError
            self.metric.value = 5.0  # type: ignore

        with self.assertRaises(ValidationError):
            self.report.project_name = "NewName"  # type: ignore

    def test_utc_timestamp_validation(self) -> None:
        """Verifies that timezone-naive or non-UTC datetimes fail validation."""
        naive_time = datetime(2026, 8, 4, 12, 0, 0)
        est_time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)  # Already UTC but check timezone type

        # 1. Naive datetime must raise ValidationError
        with self.assertRaises(ValidationError):
            QualityReport(
                project_name="Proj",
                generated_at=naive_time,
                summary=self.summary,
            )

        # 2. Offset-aware non-UTC datetime must raise ValidationError
        # Creating a non-UTC timezone
        from datetime import timedelta
        non_utc_tz = timezone(timedelta(hours=5))
        non_utc_time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=non_utc_tz)

        with self.assertRaises(ValidationError):
            QualityReport(
                project_name="Proj",
                generated_at=non_utc_time,
                summary=self.summary,
            )

    def test_metadata_immutability(self) -> None:
        """Verifies that metadata dictionaries are read-only views (MappingProxyType)."""
        # Modifying metadata dictionary keys must throw TypeError
        with self.assertRaises(TypeError):
            self.metric.metadata["new_key"] = "hack"  # type: ignore

        with self.assertRaises(TypeError):
            self.report.metadata["branch"] = "hacked"  # type: ignore

    def test_analyzer_interface(self) -> None:
        """Verifies that abstract interface cannot be directly instantiated but concrete subclass works."""
        with self.assertRaises(TypeError):
            QualityAnalyzer()  # type: ignore

        analyzer = DummyQualityAnalyzer()
        res = analyzer.analyze()
        self.assertIsInstance(res, QualityReport)
        self.assertEqual(res.project_name, "DummyProj")

    def test_deterministic_equality(self) -> None:
        """Verifies that duplicate setups produce equal objects."""
        metric2 = QualityMetric(
            name="complexity_metric",
            category=MetricCategory.COMPLEXITY,
            value=12.0,
            level=QualityLevel.GOOD,
            description="Cyclomatic complexity score",
            metadata={"max_limit": 20},
        )
        self.assertEqual(self.metric, metric2)


if __name__ == "__main__":
    unittest.main()
