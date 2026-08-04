"""Unit tests for the Technical Debt Analysis Engine."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Iterable, List

from app.technical_debt import (
    TechnicalDebtCategory,
    TechnicalDebtSeverity,
    TechnicalDebtItem,
    TechnicalDebtReport,
    TechnicalDebtRule,
    TechnicalDebtRuleRegistry,
    TechnicalDebtAnalysisEngine,
)


class StubRule(TechnicalDebtRule):
    """Stub rule yielding configured mock findings."""

    def __init__(
        self,
        rule_id: str,
        category: TechnicalDebtCategory = TechnicalDebtCategory.CODE_SMELL,
        severity: TechnicalDebtSeverity = TechnicalDebtSeverity.MEDIUM,
        effort_minutes: int = 15,
        fail_with_error: bool = False,
    ) -> None:
        self._rule_id = rule_id
        self._category = category
        self._severity = severity
        self._effort_minutes = effort_minutes
        self._fail_with_error = fail_with_error
        self.evaluated_contexts: List[Any] = []

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
        self.evaluated_contexts.append(context)
        if self._fail_with_error:
            raise RuntimeError("Evaluation crash")
        return [
            TechnicalDebtItem(
                id=f"{self._rule_id}-item-1",
                category=self._category,
                severity=self._severity,
                title=self.title,
                effort_minutes=self._effort_minutes,
            )
        ]


class TestTechnicalDebtAnalysisEngine(unittest.TestCase):
    """Verifies sequential orchestration flow, aggregate computation, context forwarding, and thread-safety."""

    def test_constructor_validation(self) -> None:
        """Verifies engine rejects None registry dependency."""
        with self.assertRaises(ValueError):
            TechnicalDebtAnalysisEngine(None)  # type: ignore

    def test_empty_registry(self) -> None:
        """Verifies report defaults on empty registered rules list."""
        registry = TechnicalDebtRuleRegistry()
        engine = TechnicalDebtAnalysisEngine(registry)

        report = engine.analyze(project_name="EmptyProj", context="Ctx")

        self.assertEqual(report.project_name, "EmptyProj")
        self.assertEqual(len(report.items), 0)
        self.assertEqual(report.summary.total_items, 0)
        self.assertEqual(report.summary.total_effort_minutes, 0)

    def test_single_rule_evaluation(self) -> None:
        """Verifies parsing, mapping, context forwarding, and aggregates compiling for a single rule."""
        registry = TechnicalDebtRuleRegistry()
        rule = StubRule("rule-size", category=TechnicalDebtCategory.MAINTAINABILITY, effort_minutes=30)
        registry.register(rule)

        engine = TechnicalDebtAnalysisEngine(registry)
        report = engine.analyze(project_name="SingleProj", context="OpaqueCtx")

        self.assertEqual(report.project_name, "SingleProj")
        self.assertEqual(len(report.items), 1)
        self.assertEqual(report.items[0].id, "rule-size-item-1")
        self.assertEqual(report.items[0].category, TechnicalDebtCategory.MAINTAINABILITY)

        # Context forwarding verify
        self.assertEqual(rule.evaluated_contexts, ["OpaqueCtx"])

        # Summary aggregates checks
        self.assertEqual(report.summary.total_items, 1)
        self.assertEqual(report.summary.total_effort_minutes, 30)
        self.assertEqual(report.summary.items_by_category[TechnicalDebtCategory.MAINTAINABILITY], 1)
        self.assertEqual(report.summary.effort_by_severity[TechnicalDebtSeverity.MEDIUM], 30)

    def test_multiple_rules_sequential_and_deterministic_order(self) -> None:
        """Verifies items aggregate from multiple rules in correct insertion order."""
        registry = TechnicalDebtRuleRegistry()
        r1 = StubRule("rule-1", effort_minutes=10)
        r2 = StubRule("rule-2", effort_minutes=20)
        registry.register(r1)
        registry.register(r2)

        engine = TechnicalDebtAnalysisEngine(registry)
        report = engine.analyze(project_name="MultiProj", context="Ctx")

        self.assertEqual(len(report.items), 2)
        # Order assertion
        self.assertEqual(report.items[0].id, "rule-1-item-1")
        self.assertEqual(report.items[1].id, "rule-2-item-1")

        self.assertEqual(report.summary.total_items, 2)
        self.assertEqual(report.summary.total_effort_minutes, 30)

    def test_exception_propagation(self) -> None:
        """Verifies evaluate exceptions propagate out directly without catch wrappers."""
        registry = TechnicalDebtRuleRegistry()
        rule = StubRule("rule-fail", fail_with_error=True)
        registry.register(rule)

        engine = TechnicalDebtAnalysisEngine(registry)
        with self.assertRaises(RuntimeError) as ctx:
            engine.analyze(project_name="FailProj", context="Ctx")
        self.assertEqual(str(ctx.exception), "Evaluation crash")

    def test_registry_isolation(self) -> None:
        """Verifies separate engines use isolated rule registries."""
        reg1 = TechnicalDebtRuleRegistry()
        reg2 = TechnicalDebtRuleRegistry()
        reg1.register(StubRule("r1"))
        reg2.register(StubRule("r2"))

        e1 = TechnicalDebtAnalysisEngine(reg1)
        e2 = TechnicalDebtAnalysisEngine(reg2)

        rep1 = e1.analyze(project_name="P1", context="Ctx")
        rep2 = e2.analyze(project_name="P2", context="Ctx")

        self.assertEqual(rep1.items[0].id, "r1-item-1")
        self.assertEqual(rep2.items[0].id, "r2-item-1")

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety lock and context mappings under concurrent analyze calls."""
        registry = TechnicalDebtRuleRegistry()
        registry.register(StubRule("r1", effort_minutes=15))
        engine = TechnicalDebtAnalysisEngine(registry)

        def run_analyze(index: int):
            return engine.analyze(project_name=f"Proj-{index}", context=f"Ctx-{index}")

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analyze, i) for i in range(50)]
            results = [f.result() for f in futures]

        self.assertEqual(len(results), 50)
        for i, res in enumerate(results):
            self.assertEqual(res.project_name, f"Proj-{i}")
            self.assertEqual(res.summary.total_effort_minutes, 15)


if __name__ == "__main__":
    unittest.main()
