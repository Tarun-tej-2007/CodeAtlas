"""Unit test suite for Scope, SymbolResolver, ResolutionVisitor, and resolution models."""

from pathlib import Path
import unittest

from app.analyzer import AnalysisContext
from app.analyzer.resolution import (
    ResolutionError,
    ResolutionResult,
    ResolvedReference,
    Scope,
    SymbolResolver,
)
from app.parser import Language, ParsedFile, TreeSitterParser
from app.parser.ast import ASTBuilder
from app.parser.modules import ModuleAnalyzer
from app.parser.symbols import Symbol, SymbolExtractor, SymbolKind


class TestSymbolResolution(unittest.TestCase):
    """Tests for Scope hierarchy, lexical shadowing, intra-file symbol resolution, and immutability."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.symbol_extractor = SymbolExtractor()
        self.module_analyzer = ModuleAnalyzer()
        self.resolver = SymbolResolver()
        self.js_parser = TreeSitterParser(Language.JAVASCRIPT)
        self.ts_parser = TreeSitterParser(Language.TYPESCRIPT)

    def _create_context(self, code: str, language: Language = Language.JAVASCRIPT, filename: str = "main.js") -> AnalysisContext:
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

    def test_scope_declaration_and_resolution(self) -> None:
        global_scope = Scope(kind="global")
        sym1 = Symbol(
            id="s1",
            name="val",
            kind=SymbolKind.VARIABLE,
            language=Language.JAVASCRIPT,
            path=Path("/repo/app.js"),
            start_line=1,
            end_line=1,
        )
        global_scope.declare(sym1)

        # Global scope resolution
        resolved = global_scope.resolve("val")
        self.assertEqual(resolved, sym1)

        # Child function scope declaration & shadowing
        fn_scope = global_scope.create_child(kind="function")
        sym2 = Symbol(
            id="s2",
            name="val",
            kind=SymbolKind.VARIABLE,
            language=Language.JAVASCRIPT,
            path=Path("/repo/app.js"),
            start_line=3,
            end_line=3,
        )
        fn_scope.declare(sym2)

        # fn_scope resolves to inner sym2
        self.assertEqual(fn_scope.resolve("val"), sym2)
        # global_scope still resolves to sym1
        self.assertEqual(global_scope.resolve("val"), sym1)

    def test_lexical_shadowing_intra_file(self) -> None:
        code = """
        const value = 1;
        function test() {
            const value = 2;
            console.log(value);
        }
        """
        context = self._create_context(code, Language.JAVASCRIPT, "shadowing.js")
        result = self.resolver.resolve(context)

        self.assertIsInstance(result, ResolutionResult)
        self.assertGreater(result.resolved_count, 0)

        # Check references for 'value'
        value_refs = [r for r in result.references if r.name == "value"]
        self.assertGreaterEqual(len(value_refs), 1)

        # Reference inside test() should resolve to line 4 declaration
        inner_ref = [r for r in value_refs if r.line > 3][0]
        self.assertTrue(inner_ref.resolved)
        self.assertIsNotNone(inner_ref.resolved_symbol_id)

    def test_function_and_class_resolution(self) -> None:
        code = """
        class UserService {
            getUser() {}
        }

        function createService() {
            return new UserService();
        }

        const service = createService();
        """
        context = self._create_context(code, Language.JAVASCRIPT, "service.js")
        result = self.resolver.resolve(context)

        service_refs = [r for r in result.references if r.name == "UserService"]
        fn_refs = [r for r in result.references if r.name == "createService"]

        self.assertGreaterEqual(len(service_refs), 1)
        self.assertGreaterEqual(len(fn_refs), 1)
        self.assertTrue(service_refs[0].resolved)
        self.assertTrue(fn_refs[0].resolved)

    def test_unresolved_identifiers(self) -> None:
        code = "console.log(unknownVariable);"
        context = self._create_context(code, Language.JAVASCRIPT, "unresolved.js")
        result = self.resolver.resolve(context)

        unresolved = [r for r in result.references if r.name == "unknownVariable"]
        self.assertEqual(len(unresolved), 1)
        self.assertFalse(unresolved[0].resolved)
        self.assertIsNone(unresolved[0].resolved_symbol_id)

    def test_empty_file_resolution(self) -> None:
        context = self._create_context("", Language.JAVASCRIPT, "empty.js")
        result = self.resolver.resolve(context)

        self.assertEqual(result.resolved_count, 0)
        self.assertEqual(result.unresolved_count, 0)
        self.assertEqual(len(result.references), 0)

    def test_resolution_models_immutability(self) -> None:
        ref = ResolvedReference(
            id="ref1",
            name="test",
            path=Path("/repo/app.js"),
            line=1,
            column=0,
            resolved_symbol_id="sym1",
            resolved=True,
        )

        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            ref.name = "modified"

    def test_resolver_error_handling(self) -> None:
        with self.assertRaises(ResolutionError):
            self.resolver.resolve(None)  # type: ignore


if __name__ == "__main__":
    unittest.main()
