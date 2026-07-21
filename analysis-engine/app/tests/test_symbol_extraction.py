"""Unit test suite for SymbolExtractor, SymbolVisitor, and symbol domain models."""

from pathlib import Path
import unittest

from app.parser import Language, ParsedFile, TreeSitterParser
from app.parser.ast import ASTBuilder
from app.parser.symbols import (
    SymbolExtractor,
    SymbolExtractionError,
    SymbolKind,
    SymbolTable,
)


class TestSymbolExtraction(unittest.TestCase):
    """Tests for symbol models, visitor extraction, and parent relationship wiring."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.extractor = SymbolExtractor()
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

    def test_function_and_variable_extraction_javascript(self) -> None:
        code = """
        const x = 10, y = 20;
        function calculateTotal(a, b) {
            let temp = a + b;
            return temp;
        }
        """
        doc = self._build_ast(code, Language.JAVASCRIPT, "main.js")
        table = self.extractor.extract(doc)

        self.assertIsInstance(table, SymbolTable)
        self.assertEqual(table.count, len(table.symbols))

        names = [s.name for s in table.symbols]
        kinds = [s.kind for s in table.symbols]

        self.assertIn("x", names)
        self.assertIn("y", names)
        self.assertIn("calculateTotal", names)
        self.assertIn(SymbolKind.FUNCTION, kinds)
        self.assertIn(SymbolKind.VARIABLE, kinds)

    def test_class_and_method_extraction_with_parent_relationship(self) -> None:
        code = """
        class UserService {
            constructor() {}
            getUser(id) {
                return id;
            }
        }
        """
        doc = self._build_ast(code, Language.JAVASCRIPT, "service.js")
        table = self.extractor.extract(doc)

        class_symbols = [s for s in table.symbols if s.kind == SymbolKind.CLASS]
        method_symbols = [s for s in table.symbols if s.kind == SymbolKind.METHOD]

        self.assertEqual(len(class_symbols), 1)
        self.assertEqual(class_symbols[0].name, "UserService")

        self.assertGreaterEqual(len(method_symbols), 1)
        for method in method_symbols:
            self.assertEqual(method.parent_symbol_id, class_symbols[0].id)

    def test_typescript_declarations_extraction(self) -> None:
        code = """
        export interface UserProfile {
            id: string;
            age: number;
        }

        export type UserID = string | number;

        export enum UserStatus {
            ACTIVE = "ACTIVE",
            INACTIVE = "INACTIVE"
        }

        export module UserNamespace {
            export const version = "1.0";
        }
        """
        doc = self._build_ast(code, Language.TYPESCRIPT, "types.ts")
        table = self.extractor.extract(doc)

        kinds = {s.kind for s in table.symbols}
        names = {s.name for s in table.symbols}

        self.assertIn(SymbolKind.INTERFACE, kinds)
        self.assertIn(SymbolKind.TYPE_ALIAS, kinds)
        self.assertIn(SymbolKind.ENUM, kinds)
        self.assertIn(SymbolKind.NAMESPACE, kinds)

        self.assertIn("UserProfile", names)
        self.assertIn("UserID", names)
        self.assertIn("UserStatus", names)
        self.assertIn("UserNamespace", names)

    def test_empty_ast_document_extraction(self) -> None:
        doc = self._build_ast("", Language.JAVASCRIPT, "empty.js")
        table = self.extractor.extract(doc)

        self.assertEqual(table.count, 0)
        self.assertEqual(len(table.symbols), 0)

    def test_deterministic_symbol_ids_and_ordering(self) -> None:
        code = "function alpha() {} function beta() {}"
        doc1 = self._build_ast(code, Language.JAVASCRIPT, "order.js")
        doc2 = self._build_ast(code, Language.JAVASCRIPT, "order.js")

        table1 = self.extractor.extract(doc1)
        table2 = self.extractor.extract(doc2)

        self.assertEqual(table1.model_dump(), table2.model_dump())
        self.assertEqual(table1.symbols[0].name, "alpha")
        self.assertEqual(table1.symbols[1].name, "beta")

    def test_symbol_model_immutability(self) -> None:
        code = "function test() {}"
        doc = self._build_ast(code, Language.JAVASCRIPT, "test.js")
        table = self.extractor.extract(doc)

        symbol = table.symbols[0]
        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            symbol.name = "modified"

    def test_extractor_error_handling(self) -> None:
        with self.assertRaises(SymbolExtractionError):
            self.extractor.extract(None)  # type: ignore


if __name__ == "__main__":
    unittest.main()
