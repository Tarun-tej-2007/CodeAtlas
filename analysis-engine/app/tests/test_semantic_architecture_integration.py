"""Unit tests for the Semantic Architecture Integration components."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Tuple

from app.scanner.models import Language
from app.semantic.enums import (
    SymbolKind,
    ScopeKind,
    ReferenceKind,
    VisibilityKind,
)
from app.semantic.models import (
    Location,
    SemanticSymbol,
    SemanticReference,
    SemanticScope,
    SemanticResult,
)
from app.architecture_analysis import (
    ArchitectureRuleType,
    ArchitectureSeverity,
    ArchitectureIssue,
    ArchitectureSemanticContext,
    SemanticArchitectureRule,
)


class MockSemanticRule(SemanticArchitectureRule):
    """Mock semantic architecture rule to verify inheritance and forwarding."""

    def __init__(self, rule_id: str) -> None:
        self._rule_id = rule_id

    @property
    def rule_id(self) -> str:
        return self._rule_id

    @property
    def rule_type(self) -> ArchitectureRuleType:
        return ArchitectureRuleType.ARCHITECTURAL_SMELL

    @property
    def severity(self) -> ArchitectureSeverity:
        return ArchitectureSeverity.MEDIUM

    @property
    def title(self) -> str:
        return "Mock Semantic Rule"

    @property
    def description(self) -> str:
        return "Tests semantic rule implementation."

    def evaluate_semantic(
        self, context: ArchitectureSemanticContext, *args, **kwargs
    ) -> Tuple[ArchitectureIssue, ...]:
        # Count all symbols as a simple test check
        symbols = context.list_all_symbols()
        issue = ArchitectureIssue(
            id=f"{self._rule_id}-issue",
            rule_type=self.rule_type,
            severity=self.severity,
            title="Semantic Rule Run",
            description=f"Counted symbols: {len(symbols)}",
            affected_symbols=tuple(sym.id for sym in symbols),
        )
        return (issue,)


class TestSemanticArchitectureIntegration(unittest.TestCase):
    """Verifies adapter query speeds, immutable properties, subclass structures, and thread safety."""

    def setUp(self) -> None:
        self.loc = Location(start_line=10, start_column=4, end_line=12, end_column=8)

        # Mock symbols
        self.symbol1 = SemanticSymbol(
            id="sym-1",
            name="class_a",
            qualified_name="pkg.module.class_a",
            kind=SymbolKind.CLASS,
            language=Language.PYTHON,
            file_path=Path("/workspace/pkg/module.py"),
            location=self.loc,
            visibility=VisibilityKind.PUBLIC,
        )
        self.symbol2 = SemanticSymbol(
            id="sym-2",
            name="func_b",
            qualified_name="pkg.module.func_b",
            kind=SymbolKind.FUNCTION,
            language=Language.PYTHON,
            file_path=Path("/workspace/pkg/module.py"),
            location=self.loc,
            visibility=VisibilityKind.PRIVATE,
        )

        # Mock reference
        self.ref = SemanticReference(
            symbol_id="sym-1",
            reference_kind=ReferenceKind.CALL,
            location=self.loc,
        )

        # Mock scope
        self.scope = SemanticScope(
            id="scope-main",
            kind=ScopeKind.BLOCK,
            symbol_ids=["sym-1", "sym-2"],
        )

        # Mock result
        self.semantic_result = SemanticResult(
            symbols=[self.symbol1, self.symbol2],
            references=[self.ref],
            scopes=[self.scope],
        )

        self.context = ArchitectureSemanticContext(self.semantic_result)

    def test_semantic_context_creation_and_queries(self) -> None:
        """Verifies context creation and individual indexed queries."""
        # 1. Symbol ID Lookup
        sym = self.context.get_symbol_by_id("sym-1")
        self.assertEqual(sym, self.symbol1)
        self.assertIsNone(self.context.get_symbol_by_id("missing"))

        # 2. Qualified Name Lookup
        sym_qn = self.context.get_symbol_by_qualified_name("pkg.module.func_b")
        self.assertEqual(sym_qn, self.symbol2)

        # 3. References query
        refs = self.context.get_references_for_symbol("sym-1")
        self.assertEqual(len(refs), 1)
        self.assertEqual(refs[0], self.ref)
        self.assertEqual(self.context.get_references_for_symbol("missing"), ())

        # 4. Scope query
        scope_res = self.context.get_scope_by_id("scope-main")
        self.assertEqual(scope_res, self.scope)

    def test_listing_utilities(self) -> None:
        """Verifies list retrieval functions."""
        self.assertEqual(self.context.list_all_symbols(), (self.symbol1, self.symbol2))
        self.assertEqual(self.context.list_all_references(), (self.ref,))
        self.assertEqual(self.context.list_all_scopes(), (self.scope,))

    def test_immutable_behavior(self) -> None:
        """Verifies returning lists are returned as immutable tuples."""
        symbols = self.context.list_all_symbols()
        self.assertIsInstance(symbols, tuple)

        with self.assertRaises(TypeError):
            symbols[0] = self.symbol2  # type: ignore

    def test_semantic_rule_inheritance_and_forwarding(self) -> None:
        """Verifies subclass type verification and evaluate wrapper conversions."""
        rule = MockSemanticRule("rule-1")
        self.assertTrue(issubclass(MockSemanticRule, SemanticArchitectureRule))

        # Test direct context passing
        issues1 = rule.evaluate(self.context)
        self.assertEqual(len(issues1), 1)
        self.assertEqual(issues1[0].affected_symbols, ("sym-1", "sym-2"))

        # Test passing raw semantic result (engine wraps it)
        issues2 = rule.evaluate(self.semantic_result)
        self.assertEqual(len(issues2), 1)
        self.assertEqual(issues2[0], issues1[0])

        # Test invalid context returns empty tuple
        self.assertEqual(rule.evaluate(None), ())
        self.assertEqual(rule.evaluate("invalid-type"), ())

    def test_deterministic_behavior(self) -> None:
        """Verifies consistent deterministic queries."""
        r1 = self.context.get_symbol_by_id("sym-1")
        r2 = self.context.get_symbol_by_id("sym-1")
        self.assertIs(r1, r2)

    def test_thread_safety(self) -> None:
        """Verifies concurrent query safety for the context adapter."""
        def run_queries():
            # Run various reads concurrently
            s = self.context.get_symbol_by_id("sym-1")
            _ = self.context.get_symbol_by_qualified_name("pkg.module.func_b")
            _ = self.context.get_references_for_symbol("sym-1")
            _ = self.context.list_all_symbols()
            return s

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_queries) for _ in range(25)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r, self.symbol1)


if __name__ == "__main__":
    unittest.main()
