"""Unit tests for the Report Exporters."""

import json
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.reporting import (
    ReportFormat,
    ReportSection,
    ReportGenerationError,
    ReportMetadata,
    ReportSectionContent,
    AnalysisReport,
    JSONReportExporter,
    MarkdownReportExporter,
    HTMLReportExporter,
)


class TestReportingExporters(unittest.TestCase):
    """Verifies output formatting, HTML escaping, markdown layouts, invalid inputs, and concurrency."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
        self.metadata = ReportMetadata(
            project_name="ExporterProj",
            generated_at=self.time_utc,
            format=ReportFormat.JSON,
            extra_info={"user": "admin", "pipeline": "v1"},
        )
        self.section_content = ReportSectionContent(
            section=ReportSection.SUMMARY,
            title="Summary Section",
            content="Summary metrics & details <script>alert(1)</script>",
        )
        self.report = AnalysisReport(
            metadata=self.metadata,
            sections={ReportSection.SUMMARY: self.section_content},
        )

        self.json_exporter = JSONReportExporter()
        self.markdown_exporter = MarkdownReportExporter()
        self.html_exporter = HTMLReportExporter()

    def test_invalid_inputs(self) -> None:
        """Verifies exporters reject None or invalid object types."""
        for exporter in (self.json_exporter, self.markdown_exporter, self.html_exporter):
            with self.assertRaises(ReportGenerationError):
                exporter.export(None)  # type: ignore
            with self.assertRaises(ReportGenerationError):
                exporter.export("invalid_type")  # type: ignore

    def test_json_exporter(self) -> None:
        """Verifies JSON output is structured, deterministic, and parses successfully."""
        out = self.json_exporter.export(self.report)
        self.assertIsInstance(out, str)

        parsed = json.loads(out)
        self.assertEqual(parsed["metadata"]["project_name"], "ExporterProj")
        self.assertEqual(parsed["sections"]["summary"]["title"], "Summary Section")

    def test_markdown_exporter(self) -> None:
        """Verifies Markdown layout structure, metadata block first, and canonical ordering."""
        out = self.markdown_exporter.export(self.report)

        # Confirm headings presence
        self.assertTrue(out.startswith("# Analysis Report: ExporterProj"))
        self.assertIn("## Metadata", out)
        self.assertIn("- **Report ID**:", out)
        self.assertIn("- **user**: admin", out)

        # Confirm section rendering
        self.assertIn("## Summary Section", out)
        self.assertIn("Summary metrics & details", out)

    def test_html_exporter(self) -> None:
        """Verifies HTML5 semantic tags, HTML escaping, and formatting."""
        out = self.html_exporter.export(self.report)

        # Basic HTML5 tags validation
        self.assertTrue(out.startswith("<!DOCTYPE html>"))
        self.assertIn('<html lang="en">', out)
        self.assertIn("<title>Analysis Report - ExporterProj</title>", out)

        # Confirm HTML escaping protects against scripting tag injections
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", out)
        self.assertNotIn("<script>", out)

        self.assertIn('<article id="summary">', out)

    def test_repeated_executions_determinism(self) -> None:
        """Verifies repeated execution on same input yields identical results."""
        out1 = self.markdown_exporter.export(self.report)
        out2 = self.markdown_exporter.export(self.report)
        self.assertEqual(out1, out2)

        out_html1 = self.html_exporter.export(self.report)
        out_html2 = self.html_exporter.export(self.report)
        self.assertEqual(out_html1, out_html2)

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety during concurrent exporter calls."""
        def run_markdown():
            return self.markdown_exporter.export(self.report)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_markdown) for _ in range(25)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertTrue(res.startswith("# Analysis Report: ExporterProj"))


if __name__ == "__main__":
    unittest.main()
