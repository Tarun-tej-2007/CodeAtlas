"""Unit test suite for DependencyAnalyzer, DependencyBuilder, and dependency models."""

from pathlib import Path
import unittest

from app.analyzer import AnalysisContext
from app.analyzer.calls import CallAnalyzer
from app.analyzer.dependencies import (
    Dependency,
    DependencyAnalysisError,
    DependencyAnalyzer,
    DependencyBuilder,
    DependencyKind,
    DependencyResult,
    ModuleDependency,
)
from app.analyzer.resolution import SymbolResolver
from app.parser import Language, ParsedFile, TreeSitterParser
from app.parser.ast import ASTBuilder
from app.parser.modules import ModuleAnalyzer
from app.parser.symbols import SymbolExtractor


class TestDependencyAnalysis(unittest.TestCase):
    """Tests for DependencyBuilder, DependencyAnalyzer, duplicate removal, and model immutability."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.symbol_extractor = SymbolExtractor()
        self.module_analyzer = ModuleAnalyzer()
        self.resolver = SymbolResolver()
        self.call_analyzer = CallAnalyzer()
        self.analyzer = DependencyAnalyzer()
        self.js_parser = TreeSitterParser(Language.JAVASCRIPT)
        self.ts_parser = TreeSitterParser(Language.TYPESCRIPT)

    def _create_context(self, code: str, language: Language = Language.JAVASCRIPT, filename: str = "app.js") -> AnalysisContext:
        parser = self.js_parser if language == Language.JAVASCRIPT else self.ts_parser
        file_path = Path(f"/repo/{filename}")
        parsed = ParsedFile(
            path=file_path,
            relative_path=Path(filename),
            language=language,
            source_code=code,
            tree=parser._ts_parser.parse(code.encode("utf-8")),
        )
        ast_doc = self.builder.build_document(parsed)
        symbols = self.symbol_extractor.extract(ast_doc)
        modules = self.module_analyzer.analyze(ast_doc)
        return AnalysisContext(
            ast_document=ast_doc,
            symbol_table=symbols,
            module_metadata=modules,
        )

    def test_function_and_module_dependency_building(self) -> None:
        code = """
        import React from 'react';
        import { useState } from 'react';

        function calc(a, b) {
            return a + b;
        }

        function main() {
            return calc(1, 2);
        }

        export default main;
        """
        context = self._create_context(code, Language.JAVASCRIPT, "main.js")
        result = self.analyzer.analyze(context)

        self.assertIsInstance(result, DependencyResult)
        self.assertGreater(result.dependency_count, 0)
        self.assertGreater(len(result.module_dependencies), 0)

        # Verify CALL dependency
        call_deps = [d for d in result.dependencies if d.kind == DependencyKind.CALL]
        self.assertEqual(len(call_deps), 1)
        self.assertTrue(call_deps[0].resolved)

        # Verify ModuleDependency import deduplication (react imported twice)
        react_mod_deps = [m for m in result.module_dependencies if m.target_module == "react"]
        self.assertEqual(len(react_mod_deps), 1)

    def test_recursive_dependency_building(self) -> None:
        code = """
        function factorial(n) {
            if (n <= 1) return 1;
            return n * factorial(n - 1);
        }
        """
        context = self._create_context(code, Language.JAVASCRIPT, "rec.js")
        result = self.analyzer.analyze(context)

        call_deps = [d for d in result.dependencies if d.kind == DependencyKind.CALL]
        self.assertEqual(len(call_deps), 1)
        self.assertEqual(call_deps[0].source_id, call_deps[0].target_id)

    def test_export_wildcard_module_dependency(self) -> None:
        code = "export * from './components';"
        context = self._create_context(code, Language.JAVASCRIPT, "export_all.js")
        result = self.analyzer.analyze(context)

        export_mod_deps = [m for m in result.module_dependencies if m.target_module == "./components"]
        self.assertEqual(len(export_mod_deps), 1)

    def test_empty_file_dependency_analysis(self) -> None:
        context = self._create_context("", Language.JAVASCRIPT, "empty.js")
        result = self.analyzer.analyze(context)

        self.assertEqual(result.dependency_count, 0)
        self.assertEqual(len(result.dependencies), 0)
        self.assertEqual(len(result.module_dependencies), 0)

    def test_dependency_models_immutability(self) -> None:
        dep = Dependency(
            id="dep1",
            source_id="s1",
            target_id="s2",
            kind=DependencyKind.CALL,
            path=Path("/repo/app.js"),
            line=1,
            resolved=True,
        )

        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            dep.source_id = "modified"

    def test_analyzer_error_handling(self) -> None:
        with self.assertRaises(DependencyAnalysisError):
            self.analyzer.analyze(None)  # type: ignore


if __name__ == "__main__":
    unittest.main()
