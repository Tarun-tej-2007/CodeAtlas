"""Unit test suite for CallAnalyzer, CallVisitor, and call models."""

from pathlib import Path
import unittest

from app.analyzer import AnalysisContext
from app.analyzer.calls import (
    CallAnalysisError,
    CallAnalysisResult,
    CallAnalyzer,
    CallKind,
    CallReference,
)
from app.analyzer.resolution import SymbolResolver
from app.parser import Language, ParsedFile, TreeSitterParser
from app.parser.ast import ASTBuilder
from app.parser.modules import ModuleAnalyzer
from app.parser.symbols import SymbolExtractor


class TestCallAnalysis(unittest.TestCase):
    """Tests for function, method, constructor, and static method call detection and caller-callee resolution."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.symbol_extractor = SymbolExtractor()
        self.module_analyzer = ModuleAnalyzer()
        self.resolver = SymbolResolver()
        self.analyzer = CallAnalyzer()
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

    def test_function_method_constructor_and_static_call_detection(self) -> None:
        code = """
        function calculate() { return 42; }

        class User {
            save() {}
        }

        class Logger {
            static log(msg) {}
        }

        function main() {
            calculate();
            const u = new User();
            u.save();
            Logger.log("info");
        }
        """
        context = self._create_context(code, Language.JAVASCRIPT, "calls.js")
        res_result = self.resolver.resolve(context)
        call_result = self.analyzer.analyze(context, resolution_result=res_result)

        self.assertIsInstance(call_result, CallAnalysisResult)
        self.assertEqual(call_result.call_count, len(call_result.calls))
        self.assertGreaterEqual(call_result.call_count, 4)

        kinds = {c.kind for c in call_result.calls}
        self.assertIn(CallKind.FUNCTION, kinds)
        self.assertIn(CallKind.CONSTRUCTOR, kinds)
        self.assertIn(CallKind.METHOD, kinds)
        self.assertIn(CallKind.STATIC_METHOD, kinds)

        # Check function call calculate()
        fn_call = next(c for c in call_result.calls if c.callee_name == "calculate")
        self.assertEqual(fn_call.kind, CallKind.FUNCTION)
        self.assertTrue(fn_call.resolved)
        self.assertIsNotNone(fn_call.caller_symbol_id)

    def test_recursive_call_caller_tracking(self) -> None:
        code = """
        function factorial(n) {
            if (n <= 1) return 1;
            return n * factorial(n - 1);
        }
        """
        context = self._create_context(code, Language.JAVASCRIPT, "recursive.js")
        res_result = self.resolver.resolve(context)
        call_result = self.analyzer.analyze(context, resolution_result=res_result)

        rec_call = next(c for c in call_result.calls if c.callee_name == "factorial")
        self.assertEqual(rec_call.kind, CallKind.FUNCTION)
        self.assertTrue(rec_call.resolved)
        self.assertEqual(rec_call.caller_symbol_id, rec_call.callee_symbol_id)

    def test_unresolved_call_detection(self) -> None:
        code = "function test() { unknownFunction(); }"
        context = self._create_context(code, Language.JAVASCRIPT, "unresolved.js")
        call_result = self.analyzer.analyze(context)

        unresolved = next(c for c in call_result.calls if c.callee_name == "unknownFunction")
        self.assertFalse(unresolved.resolved)
        self.assertIsNone(unresolved.callee_symbol_id)

    def test_empty_file_call_analysis(self) -> None:
        context = self._create_context("", Language.JAVASCRIPT, "empty.js")
        call_result = self.analyzer.analyze(context)

        self.assertEqual(call_result.call_count, 0)
        self.assertEqual(len(call_result.calls), 0)

    def test_call_models_immutability(self) -> None:
        call_ref = CallReference(
            id="call1",
            caller_symbol_id="s1",
            callee_name="foo",
            callee_symbol_id="s2",
            kind=CallKind.FUNCTION,
            path=Path("/repo/app.js"),
            line=1,
            column=0,
            resolved=True,
        )

        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            call_ref.callee_name = "modified"

    def test_analyzer_error_handling(self) -> None:
        with self.assertRaises(CallAnalysisError):
            self.analyzer.analyze(None)  # type: ignore


if __name__ == "__main__":
    unittest.main()
