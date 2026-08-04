"""Unit tests for the QualityAIContextBuilder component."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.ai_service.context import AIContextManager
from app.quality_analysis import (
    MetricCategory,
    QualityLevel,
    QualityMetric,
    QualityReport,
    QualitySummary,
    QualityAIContextBuilder,
)


class TestQualityAIContextBuilder(unittest.TestCase):
    """Verifies DTO-to-AIContext mappings, metadata preserves, ordering determinism, and concurrency."""

    def setUp(self) -> None:
        self.manager = AIContextManager()
        self.builder = QualityAIContextBuilder(self.manager)

        self.time_utc = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)

        # Standard populated test report structures
        self.m_size = QualityMetric(
            name="avg-file-size",
            category=MetricCategory.MAINTAINABILITY,
            value=150.0,
            level=QualityLevel.EXCELLENT,
            description="Size in bytes",
            metadata={"total_files": 2},
        )
        self.m_coupling = QualityMetric(
            name="avg-coupling",
            category=MetricCategory.COUPLING,
            value=2.5,
            level=QualityLevel.GOOD,
            description="Coupling density",
            metadata={"total_edges": 5},
        )

        self.summary = QualitySummary(
            overall_score=85.0,
            overall_level=QualityLevel.GOOD,
            metrics_by_category={
                MetricCategory.MAINTAINABILITY: 150.0,
                MetricCategory.COUPLING: 2.5,
            },
        )
        self.report = QualityReport(
            project_name="BuildProj",
            generated_at=self.time_utc,
            metrics=(self.m_size, self.m_coupling),
            summary=self.summary,
            metadata={"run_type": "automated"},
        )

    def test_constructor_validation(self) -> None:
        """Verifies builder validates constructor injected parameter."""
        with self.assertRaises(ValueError):
            QualityAIContextBuilder(None)  # type: ignore

    def test_empty_report_mapping(self) -> None:
        """Verifies context build defaults on empty report parameters."""
        empty_report = QualityReport(
            project_name="EmptyProj",
            generated_at=self.time_utc,
            metrics=(),
            summary=QualitySummary(overall_score=0.0, overall_level=QualityLevel.CRITICAL),
        )

        context = self.builder.build_context(empty_report)

        self.assertEqual(context.title, "Quality Analysis Context: EmptyProj")
        self.assertEqual(context.metadata["project_name"], "EmptyProj")
        self.assertEqual(context.metadata["overall_score"], 0.0)

        # Verify sections presence
        section_names = [sec.name for sec in context.sections]
        self.assertIn("Summary", section_names)
        self.assertIn("Quality Metrics", section_names)
        self.assertIn("Recommendations Input", section_names)

    def test_populated_report_mapping_and_preservation(self) -> None:
        """Verifies structured metadata values, category weight mappings, and section detail preserves."""
        context = self.builder.build_context(self.report)

        # Metadata preservation check
        self.assertEqual(context.metadata["project_name"], "BuildProj")
        self.assertEqual(context.metadata["overall_score"], 85.0)
        self.assertEqual(context.metadata["overall_level"], "good")
        self.assertEqual(context.metadata["weight_maintainability"], 150.0)

        # Sections presence and content checks
        sections_map = {sec.name: sec.content for sec in context.sections}

        self.assertIn("Project: BuildProj", sections_map["Summary"])
        self.assertIn("Overall Quality Score: 85.00", sections_map["Summary"])
        self.assertIn("maintainability: 150.00", sections_map["Summary"])

        self.assertIn("- Name: avg-file-size", sections_map["Quality Metrics"])
        self.assertIn("- Name: avg-coupling", sections_map["Quality Metrics"])

        self.assertIn("- Name: avg-file-size", sections_map["Maintainability"])
        self.assertIn("- Name: avg-coupling", sections_map["Coupling & Cohesion"])

        self.assertIn("Quality recommendation input requested for overall score 85.00", sections_map["Recommendations Input"])

    def test_deterministic_ordering(self) -> None:
        """Verifies section compilation output lists remain deterministic."""
        c1 = self.builder.build_context(self.report)
        c2 = self.builder.build_context(self.report)

        self.assertEqual(c1.title, c2.title)
        self.assertEqual(c1.metadata, c2.metadata)
        self.assertEqual(len(c1.sections), len(c2.sections))
        for s1, s2 in zip(c1.sections, c2.sections):
            self.assertEqual(s1.name, s2.name)
            self.assertEqual(s1.content, s2.content)

    def test_context_immutability(self) -> None:
        """Verifies builder treats inputs as read-only and does not mutate source report fields."""
        orig_metadata = dict(self.report.metadata)
        _ = self.builder.build_context(self.report)

        # Verify report values remain unchanged
        self.assertEqual(self.report.metadata, orig_metadata)
        self.assertEqual(self.report.project_name, "BuildProj")

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety of mapping routines under parallel context building requests."""
        def run_build():
            return self.builder.build_context(self.report)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_build) for _ in range(25)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.title, "Quality Analysis Context: BuildProj")
            self.assertEqual(res.metadata["overall_score"], 85.0)


if __name__ == "__main__":
    unittest.main()
