"""Unit tests for the Architecture Rule Framework component."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import Tuple

from app.architecture_analysis import (
    ArchitectureRuleType,
    ArchitectureSeverity,
    ArchitectureIssue,
    ArchitectureRule,
    ArchitectureRuleRegistry,
    ArchitectureRegistryError,
)


class MockArchitectureRule(ArchitectureRule):
    """Mock implementation of ArchitectureRule for testing."""

    def __init__(
        self,
        rule_id: str,
        rule_type: ArchitectureRuleType = ArchitectureRuleType.CIRCULAR_DEPENDENCY,
        severity: ArchitectureSeverity = ArchitectureSeverity.MEDIUM,
        title: str = "Mock Rule",
        description: str = "A mock rule for integration tests.",
    ) -> None:
        self._rule_id = rule_id
        self._rule_type = rule_type
        self._severity = severity
        self._title = title
        self._description = description

    @property
    def rule_id(self) -> str:
        return self._rule_id

    @property
    def rule_type(self) -> ArchitectureRuleType:
        return self._rule_type

    @property
    def severity(self) -> ArchitectureSeverity:
        return self._severity

    @property
    def title(self) -> str:
        return self._title

    @property
    def description(self) -> str:
        return self._description

    def evaluate(self, *args, **kwargs) -> Tuple[ArchitectureIssue, ...]:
        return ()


class TestArchitectureRuleFramework(unittest.TestCase):
    """Verifies duplicate registration traps, ordering retention, and concurrent access safety."""

    def setUp(self) -> None:
        self.registry = ArchitectureRuleRegistry()
        self.rule1 = MockArchitectureRule("rule-1", title="Rule One")
        self.rule2 = MockArchitectureRule("rule-2", title="Rule Two")
        self.rule3 = MockArchitectureRule("rule-3", title="Rule Three")

    def test_abstract_rule_interface(self) -> None:
        """Verifies abstract base class property accesses."""
        rule = MockArchitectureRule(
            "rule-test",
            rule_type=ArchitectureRuleType.LAYER_VIOLATION,
            severity=ArchitectureSeverity.HIGH,
            title="Layer Check",
            description="Checks layering constraints"
        )
        self.assertEqual(rule.rule_id, "rule-test")
        self.assertEqual(rule.rule_type, ArchitectureRuleType.LAYER_VIOLATION)
        self.assertEqual(rule.severity, ArchitectureSeverity.HIGH)
        self.assertEqual(rule.title, "Layer Check")
        self.assertEqual(rule.description, "Checks layering constraints")
        self.assertEqual(rule.evaluate(), ())

    def test_registration_and_retrieval(self) -> None:
        """Verifies basic rule registration, contains verification, and retrieval."""
        self.assertEqual(len(self.registry), 0)
        self.assertFalse(self.registry.contains("rule-1"))

        self.registry.register(self.rule1)
        self.assertEqual(len(self.registry), 1)
        self.assertTrue(self.registry.contains("rule-1"))

        retrieved = self.registry.get("rule-1")
        self.assertEqual(retrieved, self.rule1)

    def test_duplicate_registration_rejection(self) -> None:
        """Verifies duplicate registration raises an ArchitectureRegistryError."""
        self.registry.register(self.rule1)
        with self.assertRaises(ArchitectureRegistryError) as context:
            self.registry.register(self.rule1)
        self.assertIn("already registered", str(context.exception))

    def test_unknown_rule_retrieval_rejection(self) -> None:
        """Verifies querying unknown rules raises an ArchitectureRegistryError."""
        with self.assertRaises(ArchitectureRegistryError) as context:
            self.registry.get("unknown-id")
        self.assertIn("not registered", str(context.exception))

    def test_rule_removal_success_and_failure(self) -> None:
        """Verifies rule removal and rejection on unknown rule removals."""
        self.registry.register(self.rule1)
        self.assertTrue(self.registry.contains("rule-1"))

        # Success
        self.registry.remove("rule-1")
        self.assertFalse(self.registry.contains("rule-1"))
        self.assertEqual(len(self.registry), 0)

        # Failure
        with self.assertRaises(ArchitectureRegistryError):
            self.registry.remove("rule-1")

    def test_clear_registry(self) -> None:
        """Verifies clearing registry drops all registered rules."""
        self.registry.register(self.rule1)
        self.registry.register(self.rule2)
        self.assertEqual(len(self.registry), 2)

        self.registry.clear()
        self.assertEqual(len(self.registry), 0)

    def test_deterministic_ordering(self) -> None:
        """Verifies listing rules returns them in insertion order."""
        self.registry.register(self.rule2)
        self.registry.register(self.rule1)
        self.registry.register(self.rule3)

        rules = self.registry.list_rules()
        self.assertEqual(len(rules), 3)
        self.assertEqual(rules[0].rule_id, "rule-2")
        self.assertEqual(rules[1].rule_id, "rule-1")
        self.assertEqual(rules[2].rule_id, "rule-3")

    def test_registry_isolation(self) -> None:
        """Verifies multiple registry instances do not share state."""
        registry2 = ArchitectureRuleRegistry()

        self.registry.register(self.rule1)
        self.assertTrue(self.registry.contains("rule-1"))
        self.assertFalse(registry2.contains("rule-1"))

        registry2.register(self.rule2)
        self.assertTrue(registry2.contains("rule-2"))
        self.assertFalse(self.registry.contains("rule-2"))

    def test_concurrent_registrations_and_removals(self) -> None:
        """Verifies thread-safe execution when registry is accessed concurrently."""
        def run_thread_registration(rule_id: str) -> None:
            r = MockArchitectureRule(rule_id)
            # Register rule
            self.registry.register(r)
            # Check contains
            self.assertTrue(self.registry.contains(rule_id))
            # Retrieve rule
            retrieved = self.registry.get(rule_id)
            self.assertEqual(retrieved.rule_id, rule_id)

        rule_ids = [f"thread-rule-{i}" for i in range(100)]

        with ThreadPoolExecutor(max_workers=16) as executor:
            futures = [executor.submit(run_thread_registration, rid) for rid in rule_ids]
            # Ensure all threads completed without error
            for f in futures:
                f.result()

        self.assertEqual(len(self.registry), 100)

        # Concurrently list and remove rules
        def run_thread_removal(rule_id: str) -> None:
            # Query rules list
            _ = self.registry.list_rules()
            # Remove rule
            self.registry.remove(rule_id)

        with ThreadPoolExecutor(max_workers=16) as executor:
            futures_rem = [executor.submit(run_thread_removal, rid) for rid in rule_ids]
            for f in futures_rem:
                f.result()

        self.assertEqual(len(self.registry), 0)


if __name__ == "__main__":
    unittest.main()
