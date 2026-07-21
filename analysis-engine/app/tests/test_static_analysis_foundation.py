"""Unit test suite for static analysis foundation models, registry, and pipeline."""

from pathlib import Path
import unittest

from app.analyzer import (
    AnalysisContext,
    AnalysisError,
    AnalysisPipeline,
    AnalysisResult,
    AnalyzerExecutionError,
    AnalyzerRegistry,
    BaseAnalyzer,
    Diagnostic,
    Severity,
)
from app.parser import Language, ParsedFile, TreeSitterParser
from app.parser.ast import ASTBuilder
from app.parser.modules import ModuleAnalyzer
from app.parser.symbols import SymbolExtractor


class DummyInfoAnalyzer(BaseAnalyzer):
    """Test analyzer emitting info diagnostics."""

    def analyze(self, context: AnalysisContext) -> list[Diagnostic]:
        return [
            Diagnostic(
                id="diag_info_1",
                severity=Severity.INFO,
                message="File scanned successfully",
                path=context.ast_document.path,
                line=1,
            )
        ]


class DummyWarningAnalyzer(BaseAnalyzer):
    """Test analyzer emitting warning diagnostics."""

    def analyze(self, context: AnalysisContext) -> list[Diagnostic]:
        return [
            Diagnostic(
                id="diag_warn_1",
                severity=Severity.WARNING,
                message="Unused variable pattern detected",
                path=context.ast_document.path,
                line=5,
            )
        ]


class FailingAnalyzer(BaseAnalyzer):
    """Test analyzer that intentionally fails."""

    def analyze(self, context: AnalysisContext) -> list[Diagnostic]:
        raise RuntimeError("Simulated analyzer crash")


class TestStaticAnalysisFoundation(unittest.TestCase):
    """Tests for static analysis models, registry, pipeline execution, and exception handling."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.symbol_extractor = SymbolExtractor()
        self.module_analyzer = ModuleAnalyzer()
        self.parser = TreeSitterParser(Language.JAVASCRIPT)

    def _create_context(self, code: str, filename: str = "app.js") -> AnalysisContext:
        file_path = Path(f"/repo/{filename}")
        parsed = ParsedFile(
            path=file_path,
            relative_path=Path(filename),
            language=Language.JAVASCRIPT,
            source_code=code,
            tree=self.parser._ts_parser.parse(code.encode("utf-8")),
        )
        ast_doc = self.builder.build_document(parsed)
        symbols = self.symbol_extractor.extract(ast_doc)
        modules = self.module_analyzer.analyze(ast_doc)
        return AnalysisContext(
            ast_document=ast_doc,
            symbol_table=symbols,
            module_metadata=modules,
        )

    def test_analyzer_registry_workflow(self) -> None:
        registry = AnalyzerRegistry()
        self.assertEqual(len(registry.get_all()), 0)

        a1 = DummyInfoAnalyzer()
        a2 = DummyWarningAnalyzer()
        registry.register(a1)
        registry.register(a2)

        analyzers = registry.get_all()
        self.assertEqual(len(analyzers), 2)
        self.assertIn(a1, analyzers)
        self.assertIn(a2, analyzers)

        registry.clear()
        self.assertEqual(len(registry.get_all()), 0)

    def test_analysis_pipeline_execution_and_aggregation(self) -> None:
        context = self._create_context("const x = 10; function main() { return x; }")

        registry = AnalyzerRegistry()
        registry.register(DummyInfoAnalyzer())
        registry.register(DummyWarningAnalyzer())

        pipeline = AnalysisPipeline(registry=registry)
        result = pipeline.execute(context)

        self.assertIsInstance(result, AnalysisResult)
        self.assertEqual(len(result.diagnostics), 2)
        self.assertGreaterEqual(result.duration_ms, 0.0)

        # Verify metrics
        self.assertEqual(result.metrics["total_diagnostics"], 2)
        self.assertEqual(result.metrics["info_count"], 1)
        self.assertEqual(result.metrics["warning_count"], 1)
        self.assertEqual(result.metrics["error_count"], 0)
        self.assertGreater(result.metrics["symbols_count"], 0)

    def test_analysis_pipeline_failing_analyzer_handling(self) -> None:
        context = self._create_context("const x = 1;")

        registry = AnalyzerRegistry()
        registry.register(FailingAnalyzer())

        pipeline = AnalysisPipeline(registry=registry)

        with self.assertRaises(AnalyzerExecutionError):
            pipeline.execute(context)

        self.assertTrue(issubclass(AnalyzerExecutionError, AnalysisError))

    def test_models_immutability(self) -> None:
        context = self._create_context("const x = 1;")
        diag = Diagnostic(
            id="d1",
            severity=Severity.INFO,
            message="msg",
            path=context.ast_document.path,
            line=1,
        )

        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            diag.message = "modified"

        with self.assertRaises(ValidationError):
            context.symbol_table = None  # type: ignore


if __name__ == "__main__":
    unittest.main()
