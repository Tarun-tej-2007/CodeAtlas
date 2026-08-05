"""Unit tests for the Report AI Context Builder."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.ai_service.context import AIContextManager
from app.reporting import (
    ReportFormat,
    ReportSection,
    ReportMetadata,
    ReportSectionContent,
    AnalysisReport,
    ReportAIContextBuilder,
)


class TestReportingAIContextBuilder(unittest.TestCase):
    """Verifies report metadata mapping, section translation, layout determinism, and concurrency."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
        self.manager = AIContextManager()
        self.builder = ReportAIContextBuilder(self.manager)

        self.metadata = ReportMetadata(
            project_name="ReportAI",
            generated_at=self.time_utc,
            format=ReportFormat.MARKDOWN,
            extra_info={"env": "staging"},
        )
        self.sec = ReportSectionContent(
            section=ReportSection.SUMMARY,
            title="Overview",
            content="Summary metrics body text",
        )
        self.report = AnalysisReport(
            metadata=self.metadata,
            sections={ReportSection.SUMMARY: self.sec},
        )

    def test_invalid_inputs(self) -> None:
        """Verifies constructor validation and parameter checks reject bad values."""
        with self.assertRaises(ValueError):
            ReportAIContextBuilder(None)  # type: ignore

        with self.assertRaises(ValueError):
            self.builder.build_context(None)  # type: ignore

        with self.assertRaises(TypeError):
            self.builder.build_context("not_a_report")  # type: ignore

    def test_context_translation_and_determinism(self) -> None:
        """Verifies context is compiled deterministically with correct metadata and sections."""
        c1 = self.builder.build_context(self.report)
        c2 = self.builder.build_context(self.report)

        self.assertEqual(c1.title, "Report AI Context: ReportAI")
        self.assertEqual(c1.metadata["project_name"], "ReportAI")
        self.assertEqual(c1.metadata["meta_env"], "staging")

        sections_map = {sec.name: sec.content for sec in c1.sections}
        self.assertIn("Executive Summary Input", sections_map)
        self.assertIn("Report Metadata", sections_map)
        self.assertIn("Report Sections", sections_map)
        self.assertIn("Recommendations Input", sections_map)

        self.assertIn("### Overview (summary)", sections_map["Report Sections"])
        self.assertIn("Summary metrics body text", sections_map["Report Sections"])

        # Deterministic comparison
        self.assertEqual(c1.metadata, c2.metadata)
        self.assertEqual(len(c1.sections), len(c2.sections))
        for s1, s2 in zip(c1.sections, c2.sections):
            self.assertEqual(s1.name, s2.name)
            self.assertEqual(s1.content, s2.content)

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety during concurrent build runs."""
        def run_build():
            return self.builder.build_context(self.report)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_build) for _ in range(20)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.title, "Report AI Context: ReportAI")


if __name__ == "__main__":
    unittest.main()
