"""Unit tests for the Report Generator Registry framework."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from app.reporting import (
    ReportFormat,
    ReportGenerator,
    ReportGeneratorRegistry,
    ReportGenerationError,
    AnalysisReport,
)


class MockGenerator(ReportGenerator):
    """Mock ReportGenerator subclass for validation tests."""

    def generate(self, *, project_name: str, context: dict, format: ReportFormat, **kwargs) -> AnalysisReport:
        pass


class TestReportingFramework(unittest.TestCase):
    """Verifies thread-safe and deterministic registration, contains checks, isolation, and unregistration."""

    def setUp(self) -> None:
        self.registry = ReportGeneratorRegistry()
        self.gen1 = MockGenerator()
        self.gen2 = MockGenerator()

    def test_abstract_generator_restrictions(self) -> None:
        """Verifies that attempts to register objects that do not subclass ReportGenerator are rejected."""
        class NotAGenerator:
            pass

        with self.assertRaises(ReportGenerationError):
            self.registry.register("invalid", NotAGenerator())  # type: ignore

        with self.assertRaises(ReportGenerationError):
            self.registry.register("none", None)  # type: ignore

    def test_successful_registration_and_lookup(self) -> None:
        """Verifies register, contains, get, and len operate correctly."""
        self.assertEqual(len(self.registry), 0)
        self.assertFalse(self.registry.contains("gen1"))

        self.registry.register("gen1", self.gen1)
        self.assertEqual(len(self.registry), 1)
        self.assertTrue(self.registry.contains("gen1"))
        self.assertEqual(self.registry.get("gen1"), self.gen1)

    def test_duplicate_rejection(self) -> None:
        """Verifies duplicate generator names are rejected with ReportGenerationError."""
        self.registry.register("gen1", self.gen1)
        with self.assertRaises(ReportGenerationError):
            self.registry.register("gen1", self.gen2)

    def test_unregister(self) -> None:
        """Verifies unregistration and checks non-existent cleanups raise errors."""
        self.registry.register("gen1", self.gen1)
        self.registry.unregister("gen1")
        self.assertFalse(self.registry.contains("gen1"))
        self.assertEqual(len(self.registry), 0)

        # Unregistering missing generator raises ReportGenerationError
        with self.assertRaises(ReportGenerationError):
            self.registry.unregister("missing")

    def test_clear(self) -> None:
        """Verifies clear removes all registered entries."""
        self.registry.register("gen1", self.gen1)
        self.registry.register("gen2", self.gen2)
        self.registry.clear()
        self.assertEqual(len(self.registry), 0)

    def test_insertion_ordering_and_immutable_listing(self) -> None:
        """Verifies deterministic registration ordering and lists are frozen tuples."""
        self.registry.register("second_registered", self.gen2)
        self.registry.register("first_registered", self.gen1)

        listed = self.registry.list_generators()
        self.assertIsInstance(listed, tuple)
        self.assertEqual(listed[0], self.gen2)
        self.assertEqual(listed[1], self.gen1)

    def test_registry_isolation(self) -> None:
        """Verifies separate registry instances maintain distinct, isolated scopes."""
        other_registry = ReportGeneratorRegistry()
        self.registry.register("gen1", self.gen1)

        self.assertTrue(self.registry.contains("gen1"))
        self.assertFalse(other_registry.contains("gen1"))

    def test_concurrent_registration(self) -> None:
        """Verifies thread safety during parallel, concurrent registrations."""
        registry = ReportGeneratorRegistry()

        def run_register(index: int):
            try:
                registry.register(f"concurrent_gen_{index}", MockGenerator())
            except Exception:
                pass

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_register, i) for i in range(50)]
            for f in futures:
                f.result()

        self.assertEqual(len(registry), 50)


if __name__ == "__main__":
    unittest.main()
