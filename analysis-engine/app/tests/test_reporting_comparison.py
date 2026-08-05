"""Unit tests for the Historical Comparison Engine."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from types import MappingProxyType

from app.reporting import (
    ReportFormat,
    ReportSection,
    ReportGenerationError,
    ReportMetadata,
    ReportSectionContent,
    AnalysisReport,
    ReportComparison,
    ReportSectionDifference,
    ReportComparisonEngine,
)


class TestReportingComparison(unittest.TestCase):
    """Verifies DTO comparisons, section differences mapping, immutability, validation, and thread-safety."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
        self.engine = ReportComparisonEngine()

        self.meta_a = ReportMetadata(
            project_name="CompareProj",
            generated_at=self.time_utc,
            format=ReportFormat.JSON,
            extra_info={"pipeline": "v1", "user": "admin"},
        )
        self.sec_summary_a = ReportSectionContent(
            section=ReportSection.SUMMARY,
            title="Summary A",
            content="Summary body content A",
            metadata={"lines_scanned": 100},
        )
        self.report_a = AnalysisReport(
            metadata=self.meta_a,
            sections={ReportSection.SUMMARY: self.sec_summary_a},
        )

    def test_invalid_inputs(self) -> None:
        """Verifies validations reject None or mismatched types."""
        with self.assertRaises(ReportGenerationError):
            self.engine.compare(self.report_a, None)  # type: ignore

        with self.assertRaises(ReportGenerationError):
            self.engine.compare("not_a_report", self.report_a)  # type: ignore

    def test_identical_reports(self) -> None:
        """Verifies comparing identical reports returns metadata_changed=False and zero modifications."""
        comparison = self.engine.compare(self.report_a, self.report_a)

        self.assertIsInstance(comparison, ReportComparison)
        self.assertEqual(comparison.project_name, "CompareProj")
        self.assertFalse(comparison.metadata_changed)
        self.assertEqual(len(comparison.added_sections), 0)
        self.assertEqual(len(comparison.removed_sections), 0)
        self.assertEqual(len(comparison.modified_sections), 0)
        self.assertEqual(len(comparison.section_differences), 0)
        self.assertEqual(comparison.unchanged_sections, (ReportSection.SUMMARY,))

    def test_modified_sections(self) -> None:
        """Verifies section title, content, or metadata changes are mapped correctly."""
        sec_summary_b = ReportSectionContent(
            section=ReportSection.SUMMARY,
            title="Summary B",  # Changed title
            content="Summary body content A",  # Unchanged
            metadata={"lines_scanned": 120},  # Changed metadata
        )
        report_b = AnalysisReport(
            metadata=self.meta_a,
            sections={ReportSection.SUMMARY: sec_summary_b},
        )

        comp = self.engine.compare(self.report_a, report_b)
        self.assertEqual(comp.modified_sections, (ReportSection.SUMMARY,))
        self.assertEqual(len(comp.section_differences), 1)

        diff = comp.section_differences[ReportSection.SUMMARY]
        self.assertTrue(diff.title_changed)
        self.assertFalse(diff.content_changed)
        self.assertEqual(diff.old_content, "Summary body content A")
        self.assertEqual(diff.new_content, "Summary body content A")

        # Metadata diff checks
        self.assertEqual(
            diff.metadata_differences["lines_scanned"]["status"],
            "modified",
        )
        self.assertEqual(diff.metadata_differences["lines_scanned"]["old_value"], "100")
        self.assertEqual(diff.metadata_differences["lines_scanned"]["new_value"], "120")

    def test_added_and_removed_sections(self) -> None:
        """Verifies sections added or removed are listed deterministically."""
        sec_quality = ReportSectionContent(
            section=ReportSection.QUALITY,
            title="Quality Section",
            content="Perfect scores",
        )
        report_added = AnalysisReport(
            metadata=self.meta_a,
            sections={
                ReportSection.SUMMARY: self.sec_summary_a,
                ReportSection.QUALITY: sec_quality,
            },
        )

        comp_add = self.engine.compare(self.report_a, report_added)
        self.assertEqual(comp_add.added_sections, (ReportSection.QUALITY,))
        self.assertEqual(len(comp_add.removed_sections), 0)

        comp_rem = self.engine.compare(report_added, self.report_a)
        self.assertEqual(comp_rem.removed_sections, (ReportSection.QUALITY,))
        self.assertEqual(len(comp_rem.added_sections), 0)

    def test_metadata_changes(self) -> None:
        """Verifies metadata extra_info updates set metadata_changed flag and map key diffs."""
        meta_changed = ReportMetadata(
            project_name="CompareProj",
            generated_at=self.time_utc,
            format=ReportFormat.JSON,
            extra_info={"pipeline": "v2", "env": "prod"},  # Modified "pipeline", added "env", removed "user"
        )
        report_changed = AnalysisReport(
            metadata=meta_changed,
            sections={ReportSection.SUMMARY: self.sec_summary_a},
        )

        comp = self.engine.compare(self.report_a, report_changed)
        self.assertTrue(comp.metadata_changed)

        diffs = comp.metadata_differences
        self.assertEqual(diffs["extra_info_pipeline"]["status"], "modified")
        self.assertEqual(diffs["extra_info_pipeline"]["new_value"], "v2")
        self.assertEqual(diffs["extra_info_env"]["status"], "added")
        self.assertEqual(diffs["extra_info_user"]["status"], "removed")

    def test_repeated_executions_determinism(self) -> None:
        """Verifies repeated calls on same inputs return identical comparison fields."""
        c1 = self.engine.compare(self.report_a, self.report_a)
        c2 = self.engine.compare(self.report_a, self.report_a)

        self.assertEqual(c1.added_sections, c2.added_sections)
        self.assertEqual(c1.removed_sections, c2.removed_sections)
        self.assertEqual(c1.metadata_differences, c2.metadata_differences)

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety during concurrent comparisons calls."""
        def run_compare():
            return self.engine.compare(self.report_a, self.report_a)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_compare) for _ in range(25)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.project_name, "CompareProj")
            self.assertFalse(res.metadata_changed)


if __name__ == "__main__":
    unittest.main()
