"""Unit tests for the Dashboard Comparison subsystem."""

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
    DashboardComparisonEngine,
    DashboardComparison,
    DashboardWidgetDifference,
)


class TestDashboardComparison(unittest.TestCase):
    """Verifies widget changes detection, metadata differences, sorted outputs, and concurrency."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
        self.engine = DashboardComparisonEngine()

        # Build baseline old dashboard
        self.meta_old = DashboardMetadata(
            project_name="BaseProj",
            created_at=self.time_utc,
            status=DashboardStatus.READY,
            extra_info={"owner": "alice"},
        )
        self.w_summary_old = DashboardWidget(
            type=DashboardWidgetType.SUMMARY,
            title="Summary Widget",
            content="50 lines",
        )
        self.w_metrics_old = DashboardWidget(
            type=DashboardWidgetType.METRICS,
            title="Metrics Widget",
            content="10 files",
        )
        self.dash_old = DashboardModel(
            metadata=self.meta_old,
            widgets={
                "w_sum": self.w_summary_old,
                "w_met": self.w_metrics_old,
            },
        )

    def test_invalid_parameters(self) -> None:
        """Verifies validations reject invalid or None parameters."""
        with self.assertRaises(DashboardValidationError):
            self.engine.compare(None, self.dash_old)  # type: ignore

        with self.assertRaises(DashboardValidationError):
            self.engine.compare(self.dash_old, "not_a_dashboard")  # type: ignore

    def test_identical_dashboards(self) -> None:
        """Verifies comparing identical dashboards returns zero differences."""
        diff = self.engine.compare(self.dash_old, self.dash_old)

        self.assertIsInstance(diff, DashboardComparison)
        self.assertEqual(len(diff.added_widgets), 0)
        self.assertEqual(len(diff.removed_widgets), 0)
        self.assertEqual(len(diff.modified_widgets), 0)
        self.assertEqual(len(diff.unchanged_widgets), 2)
        self.assertEqual(len(diff.metadata_changes), 0)

    def test_added_and_removed_widgets(self) -> None:
        """Verifies that added and removed widgets are tracked deterministically."""
        # Create a new dashboard with w_sum removed and w_custom added
        w_custom = DashboardWidget(
            type=DashboardWidgetType.QUALITY,
            title="Custom Widget",
            content="Custom data",
        )
        dash_new = DashboardModel(
            metadata=self.meta_old,
            widgets={
                "w_met": self.w_metrics_old,
                "w_cust": w_custom,
            },
        )

        diff = self.engine.compare(self.dash_old, dash_new)
        self.assertEqual(diff.added_widgets, ["w_cust"])
        self.assertEqual(diff.removed_widgets, ["w_sum"])
        self.assertEqual(diff.unchanged_widgets, ["w_met"])
        self.assertEqual(len(diff.modified_widgets), 0)

    def test_modified_widgets_and_metadata(self) -> None:
        """Verifies content edits, title changes, widget metadata edits, and top-level metadata delta detections."""
        meta_new = DashboardMetadata(
            project_name="BaseProjUpdated",
            created_at=self.time_utc,
            status=DashboardStatus.READY,
            extra_info={"owner": "bob", "new_tag": "active"},
        )

        # Modify summary widget title & content
        w_summary_new = DashboardWidget(
            type=DashboardWidgetType.SUMMARY,
            title="Summary Widget Updated",
            content="150 lines",
        )
        # Modify metrics widget metadata extra entries
        w_metrics_new = DashboardWidget(
            type=DashboardWidgetType.METRICS,
            title="Metrics Widget",
            content="10 files",
            metadata={"user": "bob"},
        )

        dash_new = DashboardModel(
            metadata=meta_new,
            widgets={
                "w_sum": w_summary_new,
                "w_met": w_metrics_new,
            },
        )

        diff = self.engine.compare(self.dash_old, dash_new)

        # Verify metadata changes
        self.assertIn("project_name", diff.metadata_changes)
        self.assertEqual(diff.metadata_changes["project_name"]["old"], "BaseProj")
        self.assertEqual(diff.metadata_changes["project_name"]["new"], "BaseProjUpdated")

        self.assertIn("owner", diff.metadata_changes)
        self.assertEqual(diff.metadata_changes["owner"]["old"], "alice")
        self.assertEqual(diff.metadata_changes["owner"]["new"], "bob")

        self.assertIn("new_tag", diff.metadata_changes)
        self.assertIsNone(diff.metadata_changes["new_tag"]["old"])
        self.assertEqual(diff.metadata_changes["new_tag"]["new"], "active")

        # Verify modified widgets
        self.assertEqual(sorted(diff.modified_widgets), ["w_met", "w_sum"])

        # Check widget differences details
        w_sum_diff = diff.widget_differences["w_sum"]
        self.assertTrue(w_sum_diff.title_changed)
        self.assertTrue(w_sum_diff.content_changed)

        w_met_diff = diff.widget_differences["w_met"]
        self.assertFalse(w_met_diff.title_changed)
        self.assertFalse(w_met_diff.content_changed)
        self.assertIn("user", w_met_diff.metadata_changes)
        self.assertEqual(w_met_diff.metadata_changes["user"]["new"], "bob")

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety during concurrent delta calculations."""
        def run_compare():
            return self.engine.compare(self.dash_old, self.dash_old)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_compare) for _ in range(15)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(len(res.unchanged_widgets), 2)
            self.assertEqual(len(res.modified_widgets), 0)


if __name__ == "__main__":
    unittest.main()
