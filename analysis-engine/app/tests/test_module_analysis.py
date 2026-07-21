"""Unit test suite for ModuleAnalyzer, ModuleVisitor, and module models."""

from pathlib import Path
import unittest

from app.parser import Language, ParsedFile, TreeSitterParser
from app.parser.ast import ASTBuilder
from app.parser.modules import (
    ExportKind,
    ImportKind,
    ModuleAnalysisError,
    ModuleAnalyzer,
    ModuleMetadata,
)


class TestModuleAnalysis(unittest.TestCase):
    """Tests for import/export analysis, kinds, aliases, and model immutability."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.analyzer = ModuleAnalyzer()
        self.js_parser = TreeSitterParser(Language.JAVASCRIPT)
        self.ts_parser = TreeSitterParser(Language.TYPESCRIPT)

    def _build_ast(self, code: str, language: Language, filename: str = "app.ts"):
        parser = self.js_parser if language == Language.JAVASCRIPT else self.ts_parser
        file_path = Path(f"/repo/{filename}")
        parsed = ParsedFile(
            path=file_path,
            relative_path=Path(filename),
            language=language,
            source_code=code,
            tree=parser._ts_parser.parse(code.encode("utf-8")),
        )
        return self.builder.build_document(parsed)

    def test_import_kinds_extraction(self) -> None:
        code = """
        import React, { useState as st, useEffect } from 'react';
        import * as utils from './utils';
        import './global.css';
        """
        doc = self._build_ast(code, Language.JAVASCRIPT, "imports.js")
        meta = self.analyzer.analyze(doc)

        self.assertIsInstance(meta, ModuleMetadata)
        self.assertEqual(meta.import_count, 5)


        kinds = [imp.kind for imp in meta.imports]
        modules = [imp.module for imp in meta.imports]
        names = [imp.name for imp in meta.imports]

        self.assertIn(ImportKind.DEFAULT, kinds)
        self.assertIn(ImportKind.NAMED, kinds)
        self.assertIn(ImportKind.NAMESPACE, kinds)
        self.assertIn(ImportKind.SIDE_EFFECT, kinds)

        # Verify alias for useEffect as ue or useState as st
        st_import = next(i for i in meta.imports if i.name == "useState")
        self.assertEqual(st_import.alias, "st")

        ns_import = next(i for i in meta.imports if i.kind == ImportKind.NAMESPACE)
        self.assertEqual(ns_import.alias, "utils")
        self.assertEqual(ns_import.module, "./utils")

        side_import = next(i for i in meta.imports if i.kind == ImportKind.SIDE_EFFECT)
        self.assertEqual(side_import.module, "./global.css")

    def test_export_kinds_extraction(self) -> None:
        code = """
        export const x = 10;
        export function foo() {}
        export { a, b as c };
        export * from './components';
        export default App;
        """
        doc = self._build_ast(code, Language.JAVASCRIPT, "exports.js")
        meta = self.analyzer.analyze(doc)

        self.assertEqual(meta.export_count, 6)

        kinds = [exp.kind for exp in meta.exports]
        names = [exp.name for exp in meta.exports]

        self.assertIn(ExportKind.DEFAULT, kinds)
        self.assertIn(ExportKind.NAMED, kinds)
        self.assertIn(ExportKind.ALL, kinds)

        self.assertIn("x", names)
        self.assertIn("foo", names)
        self.assertIn("a", names)
        self.assertIn("b", names)
        self.assertIn("*", names)
        self.assertIn("default", names)

        b_export = next(e for e in meta.exports if e.name == "b")
        self.assertEqual(b_export.alias, "c")

    def test_empty_module_analysis(self) -> None:
        doc = self._build_ast("", Language.JAVASCRIPT, "empty.js")
        meta = self.analyzer.analyze(doc)

        self.assertEqual(meta.import_count, 0)
        self.assertEqual(meta.export_count, 0)
        self.assertEqual(len(meta.imports), 0)
        self.assertEqual(len(meta.exports), 0)

    def test_deterministic_ordering_and_ids(self) -> None:
        code = """
        import { alpha } from 'lib';
        import { beta } from 'lib';
        export const x = 1;
        export const y = 2;
        """
        doc1 = self._build_ast(code, Language.JAVASCRIPT, "module.js")
        doc2 = self._build_ast(code, Language.JAVASCRIPT, "module.js")

        meta1 = self.analyzer.analyze(doc1)
        meta2 = self.analyzer.analyze(doc2)

        self.assertEqual(meta1.model_dump(), meta2.model_dump())
        self.assertEqual(meta1.imports[0].name, "alpha")
        self.assertEqual(meta1.imports[1].name, "beta")

    def test_module_models_immutability(self) -> None:
        code = "import React from 'react';"
        doc = self._build_ast(code, Language.JAVASCRIPT, "test.js")
        meta = self.analyzer.analyze(doc)

        imp = meta.imports[0]
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            imp.module = "modified"

    def test_analyzer_error_handling(self) -> None:
        with self.assertRaises(ModuleAnalysisError):
            self.analyzer.analyze(None)  # type: ignore


if __name__ == "__main__":
    unittest.main()
