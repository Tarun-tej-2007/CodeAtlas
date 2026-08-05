"""Unit tests for the Report Compilation Engine."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.reporting import (
    ReportFormat,
    ReportSection,
    ReportGenerationError,
    ReportCompilationEngine,
    AnalysisReport,
)


class TestReportingEngine(unittest.TestCase):
    """Verifies empty/populated context handling, placeholder fallbacks, validation, determinism, and thread-safety."""

    def setUp(self) -> None:
        self.engine = ReportCompilationEngine()
        self.project_name = "EngineProj"

    def test_invalid_inputs(self) -> None:
        """Verifies validations reject invalid or None project names, contexts, or formats."""
        with self.assertRaises(ReportGenerationError):
            self.engine.generate(
                project_name="   ", context={}, format=ReportFormat.JSON
            )

        with self.assertRaises(ReportGenerationError):
            self.engine.generate(
                project_name="Proj", context=None, format=ReportFormat.JSON
            )

        with self.assertRaises(ReportGenerationError):
            self.engine.generate(
                project_name="Proj", context={}, format=None  # type: ignore
            )

    def test_empty_report_compilation(self) -> None:
        """Verifies compiling with empty dict placeholder structures works without failing."""
        report = self.engine.generate(
            project_name=self.project_name,
            context={},
            format=ReportFormat.JSON,
        )

        self.assertIsInstance(report, AnalysisReport)
        self.assertEqual(report.metadata.project_name, self.project_name)
        self.assertEqual(report.metadata.format, ReportFormat.JSON)

        # Assert section counts and deterministic presence
        self.assertEqual(len(report.sections), 6)
        sections_list = list(report.sections.keys())
        expected_sections = [
            ReportSection.SUMMARY,
            ReportSection.ARCHITECTURE,
            ReportSection.QUALITY,
            ReportSection.TECHNICAL_DEBT,
            ReportSection.METRICS,
            ReportSection.RECOMMENDATIONS,
        ]
        self.assertEqual(sections_list, expected_sections)

        # Assert correct empty data placeholders are returned
        self.assertEqual(report.sections[ReportSection.ARCHITECTURE].content, "No data available.")

    def test_populated_report_compilation(self) -> None:
        """Verifies compilation matches populated values and formats lists/dicts deterministically."""
        populated_context = {
            "scan_result": {"files_scanned": 150, "dirs": ["src", "test"]},
            "parse_result": {"files_parsed": 120, "errors": 0},
            "architecture_result": "arch-v2",
            "quality_result": None,
            "technical_debt_result": {"uncovered_files": ["main.py", "auth.py"], "score": 8.0},
            "metadata": {"user": "admin", "run_id": "999"},
            "recommendations": "Add unit tests to models.",
        }

        report = self.engine.generate(
            project_name=self.project_name,
            context=populated_context,
            format=ReportFormat.HTML,
        )

        self.assertEqual(report.metadata.project_name, self.project_name)

        # Metadata checks
        self.assertEqual(report.metadata.extra_info["user"], "admin")
        self.assertEqual(report.metadata.extra_info["run_id"], "999")

        # Section formatting checks
        sec_arch = report.sections[ReportSection.ARCHITECTURE]
        self.assertEqual(sec_arch.content, "arch-v2")

        sec_debt = report.sections[ReportSection.TECHNICAL_DEBT]
        # Assert dictionary key sorted alphabetically
        self.assertEqual(
            sec_debt.content,
            "score: 8.0\nuncovered_files: [auth.py, main.py]",
        )

        sec_recs = report.sections[ReportSection.RECOMMENDATIONS]
        self.assertEqual(sec_recs.content, "Add unit tests to models.")

    def test_deterministic_execution(self) -> None:
        """Verifies that multiple compilations produce identical results."""
        context = {
            "scan_result": {"z_key": 2, "a_key": 1},
            "metadata": {"user": "tester"},
        }
        r1 = self.engine.generate(
            project_name="DetProj", context=context, format=ReportFormat.MARKDOWN
        )
        r2 = self.engine.generate(
            project_name="DetProj", context=context, format=ReportFormat.MARKDOWN
        )

        self.assertEqual(r1.metadata.project_name, r2.metadata.project_name)
        self.assertEqual(r1.metadata.format, r2.metadata.format)
        self.assertEqual(r1.metadata.extra_info, r2.metadata.extra_info)

        for s in ReportSection:
            self.assertEqual(r1.sections[s].content, r2.sections[s].content)

    def test_concurrent_execution(self) -> None:
        """Verifies engine statelessness and thread-safety during concurrent generation calls."""
        context = {"scan_result": {"count": 10}}

        def run_generation():
            return self.engine.generate(
                project_name="ThreadProj",
                context=context,
                format=ReportFormat.JSON,
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_generation) for _ in range(25)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.metadata.project_name, "ThreadProj")
            self.assertEqual(
                res.sections[ReportSection.METRICS].metadata["type"],
                "scan_parse_metrics",
            )


if __name__ == "__main__":
    unittest.main()
