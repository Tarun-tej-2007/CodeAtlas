"""Unit tests for the Dashboard Subsystem Domain Foundation."""

import unittest
import uuid
from datetime import datetime, timezone
from types import MappingProxyType

from app.dashboard import (
    DashboardWidgetType,
    DashboardStatus,
    DashboardError,
    DashboardValidationError,
    DashboardMetadata,
    DashboardWidget,
    DashboardModel,
    DashboardView,
)


class DummyDashboardView(DashboardView):
    """Concrete implementation of DashboardView for testing purposes."""

    def render(self, dashboard: DashboardModel) -> str:
        return f"Rendered project: {dashboard.metadata.project_name}"


class TestDashboardDomain(unittest.TestCase):
    """Verifies DTO attributes immutability, validation constraints, mapping proxy freezes, and enums."""

    def setUp(self) -> None:
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)
        self.meta = DashboardMetadata(
            project_name="AtlasDashboard",
            created_at=self.time_utc,
            status=DashboardStatus.READY,
            extra_info={"user": "admin"},
        )
        self.widget = DashboardWidget(
            type=DashboardWidgetType.SUMMARY,
            title="Overview Widget",
            content="Summary statistics count",
            metadata={"priority": "high"},
        )
        self.dashboard = DashboardModel(
            metadata=self.meta,
            widgets={"overview": self.widget},
        )

    def test_enum_values(self) -> None:
        """Verifies enum value mappings."""
        self.assertEqual(DashboardWidgetType.SUMMARY.value, "summary")
        self.assertEqual(DashboardWidgetType.METRICS.value, "metrics")
        self.assertEqual(DashboardStatus.PENDING.value, "pending")
        self.assertEqual(DashboardStatus.READY.value, "ready")

    def test_dto_immutability(self) -> None:
        """Verifies Pydantic DTO instances are frozen and reject edits."""
        with self.assertRaises(ValidationErrorFallback := Exception):
            # Try to mutate field on Metadata DTO
            self.meta.project_name = "NewName"  # type: ignore

        with self.assertRaises(ValidationErrorFallback):
            # Try to mutate field on Widget DTO
            self.widget.title = "NewTitle"  # type: ignore

        with self.assertRaises(ValidationErrorFallback):
            # Try to mutate field on DashboardModel DTO
            self.dashboard.metadata = self.meta  # type: ignore

    def test_mapping_proxy_protections(self) -> None:
        """Verifies extra_info, widgets, and metadata dictionaries are frozen MappingProxyTypes."""
        self.assertIsInstance(self.meta.extra_info, MappingProxyType)
        self.assertIsInstance(self.widget.metadata, MappingProxyType)
        self.assertIsInstance(self.dashboard.widgets, MappingProxyType)

        with self.assertRaises(TypeError):
            self.meta.extra_info["user"] = "hacked"  # type: ignore

        with self.assertRaises(TypeError):
            self.widget.metadata["priority"] = "low"  # type: ignore

    def test_utc_timestamp_validation(self) -> None:
        """Verifies validation rejects naive timestamps and requires UTC timezone awareness."""
        with self.assertRaises(ValueError):
            DashboardMetadata(
                project_name="NaiveProj",
                created_at=datetime.now(),  # naive
                status=DashboardStatus.READY,
            )

        with self.assertRaises(ValueError):
            # Wrong timezone
            other_tz = datetime.now(timezone.utc).astimezone()
            # If local timezone happens to be UTC, let's explicitly build non-UTC
            from datetime import timedelta
            non_utc_tz = timezone(timedelta(hours=5))
            DashboardMetadata(
                project_name="NonUTCProj",
                created_at=datetime(2026, 8, 5, 12, 0, 0, tzinfo=non_utc_tz),
                status=DashboardStatus.READY,
            )

    def test_project_name_and_title_validations(self) -> None:
        """Verifies empty or whitespace-only strings are rejected."""
        with self.assertRaises(ValueError):
            DashboardMetadata(
                project_name="   ",
                created_at=self.time_utc,
                status=DashboardStatus.READY,
            )

        with self.assertRaises(ValueError):
            DashboardWidget(
                type=DashboardWidgetType.SUMMARY,
                title="",
                content="test",
            )

    def test_deterministic_equality(self) -> None:
        """Verifies that equal values result in equal DTO structures."""
        meta2 = DashboardMetadata(
            project_name="AtlasDashboard",
            created_at=self.time_utc,
            status=DashboardStatus.READY,
            extra_info={"user": "admin"},
        )
        self.assertEqual(self.meta, meta2)

    def test_exception_hierarchy(self) -> None:
        """Verifies exception hierarchy subclassing."""
        self.assertTrue(issubclass(DashboardValidationError, DashboardError))
        self.assertTrue(issubclass(DashboardError, Exception))

    def test_abstract_interface_restrictions(self) -> None:
        """Verifies abstract interface instantiation is prevented directly."""
        with self.assertRaises(TypeError):
            DashboardView()  # type: ignore

        concrete = DummyDashboardView()
        res = concrete.render(self.dashboard)
        self.assertEqual(res, "Rendered project: AtlasDashboard")


if __name__ == "__main__":
    unittest.main()
