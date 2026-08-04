"""Unit tests for the Technical Debt Rule Framework layer."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Iterable

from app.technical_debt import (
    TechnicalDebtCategory,
    TechnicalDebtSeverity,
    TechnicalDebtRuleError,
    TechnicalDebtItem,
    TechnicalDebtRule,
    TechnicalDebtRuleRegistry,
)


class DummyRule(TechnicalDebtRule):
    """Concrete implementation of TechnicalDebtRule interface for testing registry orchestration."""

    def __init__(
        self,
        rule_id: str,
        category: TechnicalDebtCategory = TechnicalDebtCategory.CODE_SMELL,
        severity: TechnicalDebtSeverity = TechnicalDebtSeverity.MEDIUM,
    ) -> None:
        self._rule_id = rule_id
        self._category = category
        self._severity = severity

    @property
    def rule_id(self) -> str:
        return self._rule_id

    @property
    def category(self) -> TechnicalDebtCategory:
        return self._category

    @property
    def severity(self) -> TechnicalDebtSeverity:
        return self._severity

    @property
    def title(self) -> str:
        return f"Title {self._rule_id}"

    @property
    def description(self) -> str:
        return f"Description {self._rule_id}"

    def evaluate(self, context: Any, **kwargs) -> Iterable[TechnicalDebtItem]:
        return ()


class TestTechnicalDebtRuleFramework(unittest.TestCase):
    """Verifies rule validation checks, registry mappings, concurrency safety, and ordering."""

    def setUp(self) -> None:
        self.registry = TechnicalDebtRuleRegistry()
        self.r1 = DummyRule("rule-1")
        self.r2 = DummyRule("rule-2")

    def test_abstract_rule_enforcement(self) -> None:
        """Verifies instantiation of base TechnicalDebtRule ABC is disallowed."""
        with self.assertRaises(TypeError):
            TechnicalDebtRule()  # type: ignore

    def test_registration_and_lookup(self) -> None:
        """Verifies simple rule registers, contains, gets, and length counts correctly."""
        self.assertEqual(len(self.registry), 0)
        self.assertFalse(self.registry.contains("rule-1"))

        self.registry.register(self.r1)

        self.assertEqual(len(self.registry), 1)
        self.assertTrue(self.registry.contains("rule-1"))
        self.assertEqual(self.registry.get("rule-1"), self.r1)

    def test_registration_validations(self) -> None:
        """Verifies registry validations reject invalid inputs."""
        with self.assertRaises(TechnicalDebtRuleError):
            self.registry.register(None)  # type: ignore

        bad_rule = DummyRule("")
        with self.assertRaises(TechnicalDebtRuleError):
            self.registry.register(bad_rule)

    def test_duplicate_registration_rejection(self) -> None:
        """Verifies registering a rule with duplicate rule_id raises error."""
        self.registry.register(self.r1)
        duplicate = DummyRule("rule-1")

        with self.assertRaises(TechnicalDebtRuleError):
            self.registry.register(duplicate)

    def test_unregister(self) -> None:
        """Verifies removing registered rules cleans up keys and lowers count."""
        self.registry.register(self.r1)
        self.assertTrue(self.registry.contains("rule-1"))

        self.registry.unregister("rule-1")

        self.assertFalse(self.registry.contains("rule-1"))
        self.assertEqual(len(self.registry), 0)

        with self.assertRaises(TechnicalDebtRuleError):
            self.registry.unregister("rule-1")

    def test_clear(self) -> None:
        """Verifies clear resets dictionary length count to zero."""
        self.registry.register(self.r1)
        self.registry.register(self.r2)
        self.assertEqual(len(self.registry), 2)

        self.registry.clear()

        self.assertEqual(len(self.registry), 0)
        self.assertFalse(self.registry.contains("rule-1"))

    def test_insertion_order_preservation(self) -> None:
        """Verifies listing rules outputs elements in registration sequence order."""
        self.registry.register(self.r2)
        self.registry.register(self.r1)

        rules = self.registry.list_rules()
        self.assertEqual(len(rules), 2)
        self.assertEqual(rules[0], self.r2)
        self.assertEqual(rules[1], self.r1)

    def test_registry_isolation(self) -> None:
        """Verifies separate registry instances maintain distinct sets of rules."""
        other_registry = TechnicalDebtRuleRegistry()
        self.registry.register(self.r1)

        self.assertTrue(self.registry.contains("rule-1"))
        self.assertFalse(other_registry.contains("rule-1"))

    def test_concurrent_registration(self) -> None:
        """Verifies thread-safety lock integrity under high parallel registration calls."""
        registry = TechnicalDebtRuleRegistry()

        def register_task(index: int):
            rule = DummyRule(f"thread-rule-{index}")
            registry.register(rule)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(register_task, i) for i in range(100)]
            for f in futures:
                f.result()

        self.assertEqual(len(registry), 100)
        for i in range(100):
            self.assertTrue(registry.contains(f"thread-rule-{i}"))


if __name__ == "__main__":
    unittest.main()
