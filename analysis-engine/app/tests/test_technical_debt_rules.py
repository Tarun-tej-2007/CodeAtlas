"""Unit tests for concrete Technical Debt Rules."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from app.scanner.models import Language
from app.semantic.enums import SymbolKind, VisibilityKind
from app.semantic.models import Location, SemanticReference
from app.semantic.project_models import (
    ProjectFile,
    ProjectSymbol,
    SymbolLocation,
    SymbolReference,
)
from app.semantic.reference_resolver import ReferenceResolutionResult, ResolvedReference
from app.technical_debt import (
    DeadCodeRule,
    DeprecatedUsageRule,
    DuplicationRule,
    TechnicalDebtRuleRegistry,
)


class MockContext:
    """Mock context encapsulating project files and reference resolution results."""

    def __init__(self, files: dict, resolved_refs: list) -> None:
        self.files = files
        self.resolved_references = resolved_refs


class TestTechnicalDebtRules(unittest.TestCase):
    """Verifies unused symbols detection, deprecations checks, duplicate code comparison, and ordering."""

    def setUp(self) -> None:
        self.loc = Location(start_line=1, start_column=0, end_line=5, end_column=10)
        self.sym_loc_utils = SymbolLocation(file_path=Path("src/utils.py"), location=self.loc)
        self.sym_loc_main = SymbolLocation(file_path=Path("src/z_main.py"), location=self.loc)

        # Build symbols
        self.s_helper = ProjectSymbol(
            id="sym-helper",
            name="helper",
            qualified_name="src.utils.helper",
            kind=SymbolKind.FUNCTION,
            location=self.sym_loc_utils,
            visibility=VisibilityKind.PUBLIC,
            metadata={"source": "def helper():\n    pass\n    pass\n    pass"},
        )
        self.s_unused = ProjectSymbol(
            id="sym-unused",
            name="unused_func",
            qualified_name="src.utils.unused_func",
            kind=SymbolKind.FUNCTION,
            location=self.sym_loc_utils,
            visibility=VisibilityKind.PUBLIC,
            metadata={"source": "def unused_func():\n    return 42"},
        )
        self.s_deprecated = ProjectSymbol(
            id="sym-old",
            name="old_api",
            qualified_name="src.utils.old_api",
            kind=SymbolKind.FUNCTION,
            location=self.sym_loc_utils,
            visibility=VisibilityKind.PUBLIC,
            metadata={"deprecated": "Use helper instead", "source": "def old_api():\n    pass"},
        )
        # Duplicate of helper
        self.s_duplicate = ProjectSymbol(
            id="sym-dup",
            name="helper_clone",
            qualified_name="src.z_main.helper_clone",
            kind=SymbolKind.FUNCTION,
            location=self.sym_loc_main,
            visibility=VisibilityKind.PUBLIC,
            metadata={"source": "def helper():\n    pass\n    pass\n    pass"},
        )

        # Setup files mapping
        self.files = {
            Path("src/utils.py"): ProjectFile(
                path=Path("src/utils.py"),
                symbols=[self.s_helper, self.s_unused, self.s_deprecated],
            ),
            Path("src/z_main.py"): ProjectFile(
                path=Path("src/z_main.py"),
                symbols=[self.s_duplicate],
            ),
        }

        # Setup resolved reference (main references helper and deprecated old_api)
        ref_helper = SymbolReference(name="helper", location=self.sym_loc_main)
        resolved_helper = ResolvedReference(reference=ref_helper, target_symbol=self.s_helper)

        ref_old = SymbolReference(name="old_api", location=self.sym_loc_main)
        resolved_old = ResolvedReference(reference=ref_old, target_symbol=self.s_deprecated)

        self.resolved_refs = [resolved_helper, resolved_old]
        self.context = MockContext(self.files, self.resolved_refs)

    def test_dead_code_detection(self) -> None:
        """Verifies unused symbols are flagged, but referenced ones are ignored."""
        rule = DeadCodeRule()
        findings = list(rule.evaluate(self.context))

        # Expected: sym-unused and sym-dup are declared but never target of resolved references
        # Let's count them
        finding_ids = [f.id for f in findings]
        self.assertIn("dead-code-sym-unused", finding_ids)
        self.assertIn("dead-code-sym-dup", finding_ids)
        self.assertNotIn("dead-code-sym-helper", finding_ids)

        unused_finding = next(f for f in findings if f.id == "dead-code-sym-unused")
        self.assertEqual(unused_finding.location_file, "src/utils.py")
        self.assertEqual(unused_finding.location_line, 1)

    def test_deprecated_usage_detection(self) -> None:
        """Verifies references to deprecated symbols generate debt findings."""
        rule = DeprecatedUsageRule()
        findings = list(rule.evaluate(self.context))

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].id, "deprecated-use-sym-old-1")
        self.assertEqual(findings[0].location_file, "src/z_main.py")
        self.assertIn("Use helper instead", findings[0].description)

    def test_duplication_detection(self) -> None:
        """Verifies identical symbol implementations are flagged as duplicate."""
        rule = DuplicationRule()
        findings = list(rule.evaluate(self.context))

        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0].id, "duplicate-code-sym-dup")
        self.assertEqual(findings[0].location_file, "src/z_main.py")
        self.assertIn("helper_clone", findings[0].title)
        self.assertIn("src/utils.py", findings[0].description)  # points to original

    def test_empty_context(self) -> None:
        """Verifies all rules handle empty/None context configurations gracefully."""
        rules = [DeadCodeRule(), DeprecatedUsageRule(), DuplicationRule()]
        for rule in rules:
            self.assertEqual(list(rule.evaluate(None)), [])
            self.assertEqual(list(rule.evaluate(MockContext({}, []))), [])

    def test_deterministic_ordering(self) -> None:
        """Verifies output lists maintain stable deterministic order."""
        rule = DeadCodeRule()
        f1 = list(rule.evaluate(self.context))
        f2 = list(rule.evaluate(self.context))
        self.assertEqual([f.id for f in f1], [f.id for f in f2])

    def test_registry_compatibility(self) -> None:
        """Verifies concrete rules register cleanly inside TechnicalDebtRuleRegistry."""
        registry = TechnicalDebtRuleRegistry()
        r1 = DeadCodeRule()
        r2 = DeprecatedUsageRule()
        r3 = DuplicationRule()

        registry.register(r1)
        registry.register(r2)
        registry.register(r3)

        self.assertEqual(len(registry), 3)
        self.assertEqual(registry.get(r1.rule_id), r1)

    def test_thread_safety_statelessness(self) -> None:
        """Verifies parallel evaluators execution maintains isolation."""
        rule = DuplicationRule()

        def eval_task():
            return list(rule.evaluate(self.context))

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(eval_task) for _ in range(30)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(len(res), 1)
            self.assertEqual(res[0].id, "duplicate-code-sym-dup")


if __name__ == "__main__":
    unittest.main()
