"""Unit tests for the Dashboard AI Context Builder."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.ai_service.context import AIContextManager
from app.dashboard import (
    DashboardStatus,
    DashboardWidgetType,
    DashboardMetadata,
    DashboardWidget,
    DashboardModel,
    DashboardAIContextBuilder,
    DashboardValidationError,
)


class TestDashboardAIContextBuilder(unittest.TestCase):
    """Verifies dashboard metadata tags mapping, widget translation ordering, and thread safety."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
        self.manager = AIContextManager()
        self.builder = DashboardAIContextBuilder(self.manager)

        self.metadata = DashboardMetadata(
            project_name="ContextDashboard",
            created_at=self.time_utc,
            status=DashboardStatus.READY,
            extra_info={"user": "tester"},
        )
        self.w1 = DashboardWidget(
            type=DashboardWidgetType.SUMMARY,
            title="Summary widget",
            content="Total lines: 500",
        )
        self.dashboard = DashboardModel(
            metadata=self.metadata,
            widgets={"w1": self.w1},
        )

    def test_invalid_inputs(self) -> None:
        """Verifies validations reject None or bad types."""
        with self.assertRaises(ValueError):
            DashboardAIContextBuilder(None)  # type: ignore

        with self.assertRaises(DashboardValidationError):
            self.builder.build_context(None)  # type: ignore

        with self.assertRaises(TypeError):
            self.builder.build_context("invalid_dashboard_dto")  # type: ignore

    def test_context_translation_and_determinism(self) -> None:
        """Verifies context translations, metadata sorting, and deterministic outputs."""
        c1 = self.builder.build_context(self.dashboard)
        c2 = self.builder.build_context(self.dashboard)

        self.assertEqual(c1.title, "Dashboard AI Context: ContextDashboard")
        self.assertEqual(c1.metadata["project_name"], "ContextDashboard")
        self.assertEqual(c1.metadata["meta_user"], "tester")

        sections_map = {sec.name: sec.content for sec in c1.sections}
        self.assertIn("Dashboard Overview", sections_map)
        self.assertIn("Dashboard Widgets", sections_map)
        self.assertIn("Dashboard Recommendations", sections_map)

        self.assertIn("### Widget: Summary widget (summary)", sections_map["Dashboard Widgets"])
        self.assertIn("Total lines: 500", sections_map["Dashboard Widgets"])

        # Determinism check
        self.assertEqual(c1.metadata, c2.metadata)
        self.assertEqual(len(c1.sections), len(c2.sections))
        for s1, s2 in zip(c1.sections, c2.sections):
            self.assertEqual(s1.name, s2.name)
            self.assertEqual(s1.content, s2.content)

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety during concurrent build runs."""
        def run_build():
            return self.builder.build_context(self.dashboard)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_build) for _ in range(15)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.title, "Dashboard AI Context: ContextDashboard")


if __name__ == "__main__":
    unittest.main()
