"""Unit tests for the Dashboard Widget Framework."""

import unittest
from concurrent.futures import ThreadPoolExecutor

from app.dashboard import (
    DashboardValidationError,
    DashboardModel,
    DashboardView,
    DashboardWidgetRegistry,
)


class MockDashboardView(DashboardView):
    """Mock DashboardView subclass for registration tests."""

    def __init__(self, key: str) -> None:
        self.key = key

    def render(self, dashboard: DashboardModel) -> str:
        return self.key


class TestDashboardFramework(unittest.TestCase):
    """Verifies widget registry DI constraints, isolation, lookup stability, and concurrency."""

    def setUp(self) -> None:
        self.registry = DashboardWidgetRegistry()
        self.view1 = MockDashboardView("v1")
        self.view2 = MockDashboardView("v2")

    def test_successful_registration_and_lookup(self) -> None:
        """Verifies simple register, unregister, contains, and get methods."""
        self.assertFalse(self.registry.contains("widget1"))
        self.registry.register("widget1", self.view1)
        self.assertTrue(self.registry.contains("widget1"))

        retrieved = self.registry.get("widget1")
        self.assertEqual(retrieved, self.view1)

        self.registry.unregister("widget1")
        self.assertFalse(self.registry.contains("widget1"))

    def test_registration_validation_rejections(self) -> None:
        """Verifies validations reject invalid views, duplicate names, or empty strings."""
        with self.assertRaises(DashboardValidationError):
            self.registry.register("   ", self.view1)

        with self.assertRaises(DashboardValidationError):
            self.registry.register("widget1", None)  # type: ignore

        with self.assertRaises(DashboardValidationError):
            self.registry.register("widget1", "not_a_view")  # type: ignore

        self.registry.register("widget1", self.view1)
        with self.assertRaises(DashboardValidationError):
            # Duplicate name registration rejection
            self.registry.register("widget1", self.view2)

    def test_unregister_rejections(self) -> None:
        """Verifies unregistering non-existent widget views raises validations error."""
        with self.assertRaises(DashboardValidationError):
            self.registry.unregister("non_existent")

        with self.assertRaises(DashboardValidationError):
            self.registry.unregister("   ")

    def test_get_rejections(self) -> None:
        """Verifies retrieving non-existent widgets raises validations error."""
        with self.assertRaises(DashboardValidationError):
            self.registry.get("missing")

        with self.assertRaises(DashboardValidationError):
            self.registry.get("   ")

    def test_clear_operation(self) -> None:
        """Verifies clear removes all entries."""
        self.registry.register("w1", self.view1)
        self.registry.register("w2", self.view2)
        self.assertEqual(len(self.registry), 2)

        self.registry.clear()
        self.assertEqual(len(self.registry), 0)
        self.assertEqual(len(self.registry.list_widgets()), 0)

    def test_insertion_ordering_and_immutable_listing(self) -> None:
        """Verifies listing returns widgets in order registered, as an immutable tuple."""
        self.registry.register("w1", self.view1)
        self.registry.register("w2", self.view2)

        listed = self.registry.list_widgets()
        self.assertIsInstance(listed, tuple)
        self.assertEqual(listed[0], self.view1)
        self.assertEqual(listed[1], self.view2)

    def test_registry_isolation(self) -> None:
        """Verifies different registry instances do not share widget storage."""
        other_registry = DashboardWidgetRegistry()
        self.registry.register("w1", self.view1)

        self.assertTrue(self.registry.contains("w1"))
        self.assertFalse(other_registry.contains("w1"))

    def test_concurrent_registration(self) -> None:
        """Verifies thread-safety during concurrent registration runs."""
        def register_task(index: int):
            view = MockDashboardView(f"v_{index}")
            self.registry.register(f"widget_{index}", view)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(register_task, i) for i in range(30)]
            for f in futures:
                f.result()

        self.assertEqual(len(self.registry), 30)


if __name__ == "__main__":
    unittest.main()
