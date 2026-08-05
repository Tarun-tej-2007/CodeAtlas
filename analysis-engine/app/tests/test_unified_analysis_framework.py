"""Unit tests for the Unified Analysis framework integration classes."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from app.unified_analysis import (
    UnifiedAnalysisAggregationError,
    UnifiedAnalysisContributor,
    UnifiedAnalysisRegistry,
)


class DummyContributor(UnifiedAnalysisContributor):
    """Concrete implementation of UnifiedAnalysisContributor for test verifications."""

    def __init__(self, name: str, category: str = "general") -> None:
        self._name = name
        self._category = category

    @property
    def contributor_name(self) -> str:
        return self._name

    @property
    def contributor_type(self) -> str:
        return self._category

    def contribute(self, context: Any, **kwargs) -> Any:
        return f"Result-{self._name}"


class TestUnifiedAnalysisFramework(unittest.TestCase):
    """Verifies registry bounds, duplicate registrations blocks, insertion order preservation, and thread-safe registry isolation."""

    def setUp(self) -> None:
        self.registry = UnifiedAnalysisRegistry()
        self.c1 = DummyContributor(name="contributor-1", category="scan")
        self.c2 = DummyContributor(name="contributor-2", category="architecture")

    def test_abstract_base_restrictions(self) -> None:
        """Verifies abstract base contributor cannot be instantiated directly."""
        with self.assertRaises(TypeError):
            UnifiedAnalysisContributor()  # type: ignore

    def test_successful_registration_and_lookup(self) -> None:
        """Verifies contributors can be registered and retrieved by name."""
        self.assertEqual(len(self.registry), 0)

        self.registry.register(self.c1)
        self.assertEqual(len(self.registry), 1)
        self.assertTrue(self.registry.contains("contributor-1"))

        retrieved = self.registry.get("contributor-1")
        self.assertEqual(retrieved, self.c1)

    def test_duplicate_rejection(self) -> None:
        """Verifies duplicate registration attempts throw UnifiedAnalysisAggregationError."""
        self.registry.register(self.c1)
        with self.assertRaises(UnifiedAnalysisAggregationError):
            self.registry.register(self.c1)

        c1_dup = DummyContributor(name="contributor-1", category="other")
        with self.assertRaises(UnifiedAnalysisAggregationError):
            self.registry.register(c1_dup)

    def test_invalid_registrations_rejection(self) -> None:
        """Verifies None or non-contributor registrations are rejected."""
        with self.assertRaises(UnifiedAnalysisAggregationError):
            self.registry.register(None)  # type: ignore

        with self.assertRaises(UnifiedAnalysisAggregationError):
            self.registry.register("invalid-type")  # type: ignore

        blank_name_contributor = DummyContributor(name="   ")
        with self.assertRaises(UnifiedAnalysisAggregationError):
            self.registry.register(blank_name_contributor)

    def test_contains_and_unregister(self) -> None:
        """Verifies contains checks and unregistration behavior."""
        self.registry.register(self.c1)
        self.assertTrue(self.registry.contains("contributor-1"))

        self.registry.unregister("contributor-1")
        self.assertFalse(self.registry.contains("contributor-1"))
        self.assertEqual(len(self.registry), 0)

        # Unregistering non-existent throws
        with self.assertRaises(UnifiedAnalysisAggregationError):
            self.registry.unregister("non-existent")

    def test_clear_method(self) -> None:
        """Verifies clearing registry removes all registered contributors."""
        self.registry.register(self.c1)
        self.registry.register(self.c2)
        self.assertEqual(len(self.registry), 2)

        self.registry.clear()
        self.assertEqual(len(self.registry), 0)

    def test_insertion_order_preservation(self) -> None:
        """Verifies deterministic insertion order preservation inside list output collections."""
        self.registry.register(self.c2)
        self.registry.register(self.c1)

        listed = self.registry.list_contributors()
        self.assertEqual(len(listed), 2)
        self.assertEqual(listed[0], self.c2)
        self.assertEqual(listed[1], self.c1)

    def test_registry_isolation(self) -> None:
        """Verifies separate instances of registries do not share state."""
        other_registry = UnifiedAnalysisRegistry()
        self.registry.register(self.c1)

        self.assertTrue(self.registry.contains("contributor-1"))
        self.assertFalse(other_registry.contains("contributor-1"))

    def test_concurrent_registrations(self) -> None:
        """Verifies thread safety during parallel registration runs."""
        registry = UnifiedAnalysisRegistry()

        def register_concurrently(idx: int):
            c = DummyContributor(name=f"thread-contributor-{idx}")
            registry.register(c)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(register_concurrently, i) for i in range(50)]
            for f in futures:
                f.result()

        self.assertEqual(len(registry), 50)


if __name__ == "__main__":
    unittest.main()
