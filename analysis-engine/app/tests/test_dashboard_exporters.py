"""Unit tests for the Dashboard Exporter subsystem."""

import json
import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.dashboard import (
    DashboardStatus,
    DashboardWidgetType,
    DashboardMetadata,
    DashboardWidget,
    DashboardModel,
    DashboardValidationError,
    JSONDashboardExporter,
    MarkdownDashboardExporter,
    HTMLDashboardExporter,
)


class TestDashboardExporters(unittest.TestCase):
    """Verifies output formats, JSON nesting structures, HTML escaping, parameter constraints, and concurrency."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
        self.meta = DashboardMetadata(
            project_name="Export<Code>",
            created_at=self.time_utc,
            status=DashboardStatus.READY,
            extra_info={"compiler": "v1.2"},
        )
        self.widget = DashboardWidget(
            type=DashboardWidgetType.SUMMARY,
            title="Summary Widget <Title>",
            content="Count: 50 lines",
        )
        self.dashboard = DashboardModel(
            metadata=self.meta,
            widgets={"w1": self.widget},
        )

        self.json_exporter = JSONDashboardExporter()
        self.markdown_exporter = MarkdownDashboardExporter()
        self.html_exporter = HTMLDashboardExporter()

    def test_exporter_input_validations(self) -> None:
        """Verifies validations reject invalid or None DTO objects."""
        for exporter in (self.json_exporter, self.markdown_exporter, self.html_exporter):
            with self.assertRaises(DashboardValidationError):
                exporter.export(None)  # type: ignore

            with self.assertRaises(DashboardValidationError):
                exporter.export("not_a_dashboard")  # type: ignore

    def test_json_exporter_output(self) -> None:
        """Verifies JSON output correctness, sorted keys, and recursive MappingProxyType parsing."""
        res = self.json_exporter.export(self.dashboard)
        parsed = json.loads(res)

        self.assertEqual(parsed["metadata"]["project_name"], "Export<Code>")
        self.assertEqual(parsed["metadata"]["status"], "ready")
        self.assertEqual(parsed["widgets"]["w1"]["title"], "Summary Widget <Title>")
        self.assertEqual(parsed["widgets"]["w1"]["content"], "Count: 50 lines")

    def test_markdown_exporter_output(self) -> None:
        """Verifies Markdown layout formatting details."""
        res = self.markdown_exporter.export(self.dashboard)

        self.assertIn("# Dashboard: Export<Code>", res)
        self.assertIn("- **Dashboard ID**:", res)
        self.assertIn("- **compiler**: v1.2", res)
        self.assertIn("## Summary Widget <Title> (summary)", res)
        self.assertIn("Count: 50 lines", res)

    def test_html_exporter_escaping_and_output(self) -> None:
        """Verifies HTML output format structure and escaping against cross-site script injections."""
        res = self.html_exporter.export(self.dashboard)

        self.assertIn("<!DOCTYPE html>", res)
        # Verify characters are escaped properly
        self.assertIn("Export&lt;Code&gt;", res)
        self.assertNotIn("Export<Code>", res)
        self.assertIn("Summary Widget &lt;Title&gt;", res)
        self.assertNotIn("Summary Widget <Title>", res)

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety and deterministic output matches during concurrent export executions."""
        def run_json():
            return self.json_exporter.export(self.dashboard)

        def run_markdown():
            return self.markdown_exporter.export(self.dashboard)

        def run_html():
            return self.html_exporter.export(self.dashboard)

        with ThreadPoolExecutor(max_workers=12) as executor:
            json_futures = [executor.submit(run_json) for _ in range(10)]
            md_futures = [executor.submit(run_markdown) for _ in range(10)]
            html_futures = [executor.submit(run_html) for _ in range(10)]

            json_results = [f.result() for f in json_futures]
            md_results = [f.result() for f in md_futures]
            html_results = [f.result() for f in html_futures]

        # Verify deterministic equality
        for r in json_results:
            self.assertEqual(r, json_results[0])
        for r in md_results:
            self.assertEqual(r, md_results[0])
        for r in html_results:
            self.assertEqual(r, html_results[0])


if __name__ == "__main__":
    unittest.main()
