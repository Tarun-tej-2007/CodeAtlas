"""Comprehensive performance, robustness, timing, and memory stability test suite for the static analysis pipeline."""

from pathlib import Path
import tempfile
import unittest

from app.analyzer import (
    AnalysisContext,
    AnalysisPipeline,
    AnalysisResult,
    AnalyzerRegistry,
    BaseAnalyzer,
    Diagnostic,
    Severity,
)
from app.analyzer.calls import CallAnalyzer
from app.analyzer.dependencies import DependencyAnalyzer
from app.analyzer.resolution import SymbolResolver
from app.analyzer.rules import BaseRule, RuleEngine, RuleRegistry
from app.parser import Language, ParsedFile, RepositoryParser, TreeSitterParser
from app.parser.ast import ASTBuilder
from app.parser.modules import ModuleAnalyzer
from app.parser.symbols import SymbolExtractor
from app.scanner import Scanner


class CrashingAnalyzer(BaseAnalyzer):
    """Test analyzer that deliberately raises an exception."""

    def analyze(self, context: AnalysisContext) -> list[Diagnostic]:
        raise RuntimeError("Simulated analyzer crash")


class CrashingRule(BaseRule):
    """Test rule that deliberately raises an exception."""

    def evaluate(self, context: AnalysisContext, **kwargs) -> list[Diagnostic]:
        raise RuntimeError("Simulated rule crash")


class TestAnalysisPipelineOptimization(unittest.TestCase):
    """Test suite covering pipeline robustness, performance, memory stability, and timing metrics."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.symbol_extractor = SymbolExtractor()
        self.module_analyzer = ModuleAnalyzer()
        self.resolver = SymbolResolver()
        self.call_analyzer = CallAnalyzer()
        self.dep_analyzer = DependencyAnalyzer()
        self.rule_engine = RuleEngine()
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

    def test_analyzer_failure_isolation(self) -> None:
        context = self._create_context("const x = 10;")
        registry = AnalyzerRegistry()
        registry.register(CrashingAnalyzer())

        pipeline = AnalysisPipeline(registry=registry)
        result = pipeline.execute(context)

        self.assertIsInstance(result, AnalysisResult)
        self.assertEqual(len(result.diagnostics), 1)
        self.assertEqual(result.diagnostics[0].severity, Severity.ERROR)
        self.assertIn("Simulated analyzer crash", result.diagnostics[0].message)

    def test_rule_failure_isolation(self) -> None:
        context = self._create_context("const x = 10;")
        rule_registry = RuleRegistry()
        rule_registry.register(CrashingRule())

        engine = RuleEngine(registry=rule_registry)
        diagnostics = engine.execute(context)

        self.assertEqual(len(diagnostics), 1)
        self.assertEqual(diagnostics[0].severity, Severity.ERROR)
        self.assertIn("Simulated rule crash", diagnostics[0].message)

    def test_extended_performance_metrics(self) -> None:
        context = self._create_context("const a = 1; const b = 2;")
        pipeline = AnalysisPipeline()
        result = pipeline.execute(context)

        self.assertIn("total_duration_ms", result.metrics)
        self.assertIn("analyzer_durations", result.metrics)
        self.assertIn("number_of_diagnostics", result.metrics)
        self.assertGreaterEqual(result.metrics["total_duration_ms"], 0.0)

    def test_large_repository_simulation_scale(self) -> None:
        """Simulates analyzing hundreds of files and thousands of symbols/dependencies."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            root = Path(tmp_dir).resolve()
            src = root / "src"
            src.mkdir()

            # Create 100 modules with symbols and calls
            for i in range(100):
                code = f"""
                import {{ helper_{i} }} from './helper';
                export function action_{i}() {{
                    const val_{i} = {i};
                    return val_{i} + 1;
                }}
                """
                (src / f"module_{i}.js").write_text(code)

            scanner = Scanner(root)
            scan_res = scanner.scan()

            repo_parser = RepositoryParser()
            parse_res = repo_parser.parse(scan_res)

            total_symbols = 0
            total_deps = 0

            # Execute full pipeline over all files
            for parsed_file in parse_res.files:
                ast_doc = self.builder.build_document(parsed_file)
                symbols = self.symbol_extractor.extract(ast_doc)
                modules = self.module_analyzer.analyze(ast_doc)
                ctx = AnalysisContext(ast_document=ast_doc, symbol_table=symbols, module_metadata=modules)

                res = self.resolver.resolve(ctx)
                calls = self.call_analyzer.analyze(ctx, res)
                deps = self.dep_analyzer.analyze(ctx, res, calls)

                total_symbols += symbols.count
                total_deps += deps.dependency_count

            self.assertGreaterEqual(total_symbols, 100)
            self.assertGreaterEqual(total_deps, 100)

    def test_deterministic_output_and_ordering(self) -> None:
        code = "const b = 2; const a = 1; function test() { return a + b; }"
        context1 = self._create_context(code)
        context2 = self._create_context(code)

        res1 = self.resolver.resolve(context1)
        res2 = self.resolver.resolve(context2)

        calls1 = self.call_analyzer.analyze(context1, res1)
        calls2 = self.call_analyzer.analyze(context2, res2)

        deps1 = self.dep_analyzer.analyze(context1, res1, calls1)
        deps2 = self.dep_analyzer.analyze(context2, res2, calls2)

        self.assertEqual(res1.model_dump(), res2.model_dump())
        self.assertEqual(calls1.model_dump(), calls2.model_dump())
        self.assertEqual(deps1.model_dump(), deps2.model_dump())


if __name__ == "__main__":
    unittest.main()
