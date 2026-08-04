"""Unit tests for the ArchitectureRuleEngine component."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Tuple

from app.architecture_analysis import (
    ArchitectureRuleType,
    ArchitectureSeverity,
    ArchitectureIssue,
    ArchitectureRule,
    ArchitectureRuleRegistry,
    ArchitectureRuleEngine,
)
from app.architecture_analysis.exceptions import ArchitectureRuleError


class DummyRule(ArchitectureRule):
    """Dummy rule implementation returning mock issues for testing."""

    def __init__(
        self,
        rule_id: str,
        issues: Tuple[ArchitectureIssue, ...],
        should_fail: bool = False,
    ) -> None:
        self._rule_id = rule_id
        self._issues = issues
        self._should_fail = should_fail
        self.last_evaluated_context = None

    @property
    def rule_id(self) -> str:
        return self._rule_id

    @property
    def rule_type(self) -> ArchitectureRuleType:
        return ArchitectureRuleType.CIRCULAR_DEPENDENCY

    @property
    def severity(self) -> ArchitectureSeverity:
        return ArchitectureSeverity.MEDIUM

    @property
    def title(self) -> str:
        return "Dummy Rule"

    @property
    def description(self) -> str:
        return "Used for rule engine testing."

    def evaluate(self, *args, **kwargs) -> Tuple[ArchitectureIssue, ...]:
        self.last_evaluated_context = args[0] if args else kwargs.get("context")
        if self._should_fail:
            raise ArchitectureRuleError(f"Rule {self._rule_id} crashed during evaluation.")
        return self._issues


class TestArchitectureRuleEngine(unittest.TestCase):
    """Verifies orchestration sequence, metric counts, context forwarding, and concurrency properties."""

    def setUp(self) -> None:
        self.registry = ArchitectureRuleRegistry()
        self.engine = ArchitectureRuleEngine(self.registry)

        self.issue_info = ArchitectureIssue(
            id="iss-info",
            rule_type=ArchitectureRuleType.UNUSED_SYMBOL,
            severity=ArchitectureSeverity.INFO,
            title="Unused Symbol Info",
            description="Info description",
        )
        self.issue_high = ArchitectureIssue(
            id="iss-high",
            rule_type=ArchitectureRuleType.LAYER_VIOLATION,
            severity=ArchitectureSeverity.HIGH,
            title="Layer Violation",
            description="High description",
        )

    def test_empty_registry(self) -> None:
        """Verifies report structure when registry is empty."""
        report = self.engine.analyze(project_name="EmptyProj", context="OpaqueContext")

        self.assertEqual(report.project_name, "EmptyProj")
        self.assertEqual(len(report.issues), 0)
        self.assertEqual(report.summary.total_issues, 0)
        self.assertEqual(report.summary.info_count, 0)
        self.assertEqual(report.summary.high_count, 0)

        # Datetime must be timezone aware UTC
        self.assertIsNotNone(report.generated_at.tzinfo)
        self.assertEqual(report.generated_at.tzinfo, timezone.utc)

    def test_single_rule_evaluation(self) -> None:
        """Verifies execution of a single rule."""
        rule = DummyRule("rule-1", (self.issue_info,))
        self.registry.register(rule)

        report = self.engine.analyze(project_name="SingleRuleProj", context="MyContext")

        self.assertEqual(len(report.issues), 1)
        self.assertEqual(report.issues[0], self.issue_info)
        self.assertEqual(report.summary.total_issues, 1)
        self.assertEqual(report.summary.info_count, 1)
        self.assertEqual(report.summary.high_count, 0)
        self.assertEqual(rule.last_evaluated_context, "MyContext")

    def test_multiple_rules_and_execution_order(self) -> None:
        """Verifies sequence ordering during execution of multiple rules."""
        rule1 = DummyRule("rule-1", (self.issue_info,))
        rule2 = DummyRule("rule-2", (self.issue_high,))
        self.registry.register(rule1)
        self.registry.register(rule2)

        report = self.engine.analyze(project_name="MultiProj", context="SharedContext")

        # Order must match registration order
        self.assertEqual(len(report.issues), 2)
        self.assertEqual(report.issues[0], self.issue_info)
        self.assertEqual(report.issues[1], self.issue_high)

        # Summary count verifies aggregation
        self.assertEqual(report.summary.total_issues, 2)
        self.assertEqual(report.summary.info_count, 1)
        self.assertEqual(report.summary.high_count, 1)

        self.assertEqual(rule1.last_evaluated_context, "SharedContext")
        self.assertEqual(rule2.last_evaluated_context, "SharedContext")

    def test_exception_propagation(self) -> None:
        """Verifies rule crashes propagate directly without wrapping."""
        rule_ok = DummyRule("rule-ok", (self.issue_info,))
        rule_bad = DummyRule("rule-bad", (), should_fail=True)
        self.registry.register(rule_ok)
        self.registry.register(rule_bad)

        with self.assertRaises(ArchitectureRuleError) as context:
            self.engine.analyze(project_name="CrashedProj", context="Context")
        self.assertIn("crashed during evaluation", str(context.exception))

    def test_context_forwarding_preserves_context(self) -> None:
        """Verifies the context object is passed unchanged to rules."""
        complex_context = {"code_base": "root", "modules": ["a", "b"]}
        rule = DummyRule("rule-1", ())
        self.registry.register(rule)

        self.engine.analyze(project_name="ContextProj", context=complex_context)
        self.assertEqual(rule.last_evaluated_context, complex_context)

    def test_multiple_engine_instances_isolation(self) -> None:
        """Verifies multiple engine instances remain isolated."""
        registry2 = ArchitectureRuleRegistry()
        engine2 = ArchitectureRuleEngine(registry2)

        rule1 = DummyRule("rule-1", (self.issue_info,))
        self.registry.register(rule1)

        rule2 = DummyRule("rule-2", (self.issue_high,))
        registry2.register(rule2)

        report1 = self.engine.analyze(project_name="Proj1", context="Ctx")
        report2 = engine2.analyze(project_name="Proj2", context="Ctx")

        self.assertEqual(len(report1.issues), 1)
        self.assertEqual(report1.issues[0].id, "iss-info")

        self.assertEqual(len(report2.issues), 1)
        self.assertEqual(report2.issues[0].id, "iss-high")

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safe execution when engines are invoked concurrently."""
        rule = DummyRule("rule-1", (self.issue_info, self.issue_high))
        self.registry.register(rule)

        def run_analysis():
            return self.engine.analyze(project_name="ConcurrentProj", context="Ctx")

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analysis) for _ in range(25)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r.summary.total_issues, 2)
            self.assertEqual(r.summary.info_count, 1)
            self.assertEqual(r.summary.high_count, 1)

    def test_deterministic_behavior(self) -> None:
        """Verifies the output reports are identical for identical inputs."""
        rule1 = DummyRule("rule-1", (self.issue_info,))
        rule2 = DummyRule("rule-2", (self.issue_high,))
        self.registry.register(rule1)
        self.registry.register(rule2)

        r1 = self.engine.analyze(project_name="DetProj", context="Ctx")
        r2 = self.engine.analyze(project_name="DetProj", context="Ctx")

        # Report equality except generated_at time
        self.assertEqual(r1.project_name, r2.project_name)
        self.assertEqual(r1.issues, r2.issues)
        self.assertEqual(r1.summary, r2.summary)


if __name__ == "__main__":
    unittest.main()
