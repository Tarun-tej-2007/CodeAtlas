"""Unit test suite for Quality Rules Engine, RuleRegistry, and built-in rules."""

from pathlib import Path
import unittest

from app.analyzer import AnalysisContext, Severity
from app.analyzer.calls import CallAnalyzer
from app.analyzer.dependencies import DependencyAnalyzer
from app.analyzer.resolution import SymbolResolver
from app.analyzer.rules import (
    DuplicateExportsRule,
    DuplicateImportsRule,
    RuleEngine,
    RuleEngineError,
    RuleRegistry,
    SelfDependencyRule,
    UnresolvedCallsRule,
    UnresolvedSymbolsRule,
    UnusedImportsRule,
    UnusedSymbolsRule,
)
from app.parser import Language, ParsedFile, TreeSitterParser
from app.parser.ast import ASTBuilder
from app.parser.modules import ModuleAnalyzer
from app.parser.symbols import SymbolExtractor


class TestQualityRules(unittest.TestCase):
    """Tests for individual static quality rules, RuleRegistry, and RuleEngine execution."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.symbol_extractor = SymbolExtractor()
        self.module_analyzer = ModuleAnalyzer()
        self.resolver = SymbolResolver()
        self.call_analyzer = CallAnalyzer()
        self.dep_analyzer = DependencyAnalyzer()
        self.engine = RuleEngine()
        self.js_parser = TreeSitterParser(Language.JAVASCRIPT)

    def _create_context(self, code: str, filename: str = "app.js") -> AnalysisContext:
        file_path = Path(f"/repo/{filename}")
        parsed = ParsedFile(
            path=file_path,
            relative_path=Path(filename),
            language=Language.JAVASCRIPT,
            source_code=code,
            tree=self.js_parser._ts_parser.parse(code.encode("utf-8")),
        )
        ast_doc = self.builder.build_document(parsed)
        symbols = self.symbol_extractor.extract(ast_doc)
        modules = self.module_analyzer.analyze(ast_doc)
        return AnalysisContext(
            ast_document=ast_doc,
            symbol_table=symbols,
            module_metadata=modules,
        )

    def test_unused_symbols_rule(self) -> None:
        code = "const unusedVar = 10; function main() { return 1; }"
        context = self._create_context(code)
        res = self.resolver.resolve(context)
        calls = self.call_analyzer.analyze(context, res)
        deps = self.dep_analyzer.analyze(context, res, calls)

        rule = UnusedSymbolsRule()
        diagnostics = rule.evaluate(context, deps, res, calls)

        unused_diags = [d for d in diagnostics if "unusedVar" in d.message]
        self.assertEqual(len(unused_diags), 1)
        self.assertEqual(unused_diags[0].severity, Severity.WARNING)

    def test_unused_imports_rule(self) -> None:
        code = "import { unusedFunc } from 'lib'; const x = 1;"
        context = self._create_context(code)
        res = self.resolver.resolve(context)

        rule = UnusedImportsRule()
        diagnostics = rule.evaluate(context, resolution_result=res)

        unused_imp_diags = [d for d in diagnostics if "unusedFunc" in d.message]
        self.assertEqual(len(unused_imp_diags), 1)

    def test_duplicate_imports_rule(self) -> None:
        code = "import { a } from 'module'; import { b } from 'module';"
        context = self._create_context(code)

        rule = DuplicateImportsRule()
        diagnostics = rule.evaluate(context)

        dup_diags = [d for d in diagnostics if "module" in d.message]
        self.assertEqual(len(dup_diags), 1)
        self.assertEqual(dup_diags[0].severity, Severity.INFO)

    def test_duplicate_exports_rule(self) -> None:
        code = "const item = 1; export { item }; export { item };"
        context = self._create_context(code)

        rule = DuplicateExportsRule()
        diagnostics = rule.evaluate(context)

        dup_exp = [d for d in diagnostics if "item" in d.message]
        self.assertEqual(len(dup_exp), 1)

    def test_unresolved_symbols_and_calls_rules(self) -> None:
        code = "console.log(unknownVar); unknownCall();"
        context = self._create_context(code)
        res = self.resolver.resolve(context)
        calls = self.call_analyzer.analyze(context, res)

        sym_rule = UnresolvedSymbolsRule()
        sym_diags = sym_rule.evaluate(context, resolution_result=res)
        self.assertTrue(any("unknownVar" in d.message for d in sym_diags))

        call_rule = UnresolvedCallsRule()
        call_diags = call_rule.evaluate(context, call_result=calls)
        self.assertTrue(any("unknownCall" in d.message for d in call_diags))

    def test_self_dependency_rule_excludes_recursive_calls(self) -> None:
        code = "function rec(n) { if (n > 0) rec(n - 1); }"
        context = self._create_context(code)
        res = self.resolver.resolve(context)
        calls = self.call_analyzer.analyze(context, res)
        deps = self.dep_analyzer.analyze(context, res, calls)

        rule = SelfDependencyRule()
        diagnostics = rule.evaluate(context, dependency_result=deps)

        # Valid recursive call should NOT trigger self-dependency error
        self.assertEqual(len(diagnostics), 0)

    def test_rule_engine_full_execution(self) -> None:
        code = "const unused = 1; import { a } from 'mod'; import { b } from 'mod';"
        context = self._create_context(code)
        res = self.resolver.resolve(context)
        calls = self.call_analyzer.analyze(context, res)
        deps = self.dep_analyzer.analyze(context, res, calls)

        diagnostics = self.engine.execute(context, deps, res, calls)
        self.assertGreater(len(diagnostics), 0)

    def test_empty_file_rule_execution(self) -> None:
        context = self._create_context("")
        diagnostics = self.engine.execute(context)
        self.assertEqual(len(diagnostics), 0)

    def test_rule_engine_error_handling(self) -> None:
        with self.assertRaises(RuleEngineError):
            self.engine.execute(None)  # type: ignore


if __name__ == "__main__":
    unittest.main()
