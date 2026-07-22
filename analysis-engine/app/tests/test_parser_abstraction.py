"""Unit tests for SourceCodeParser and associated parsing exceptions."""

import unittest
from typing import Any

from app.scanner.models import Language
from app.parser import (
    SourceCodeParser,
    ParserError,
    ParserInitializationError,
    ParseError,
    UnsupportedLanguageError,
)


class DummyParser(SourceCodeParser):
    """Stub implementation of SourceCodeParser for unit testing."""

    @property
    def parser_id(self) -> str:
        return "dummy-parser-id"

    @property
    def language(self) -> Language:
        return Language.PYTHON

    def parse(self, source_code: str) -> Any:
        if not source_code:
            raise ParseError("Source code cannot be empty.")
        return {"ast": "dummy-tree", "code": source_code}


class TestParserAbstraction(unittest.TestCase):
    """Tests properties, exception inheritance, and implementation constraints of the abstraction."""

    def test_abstract_parser_cannot_be_instantiated(self) -> None:
        # 1. Abstract parser cannot be instantiated directly
        with self.assertRaises(TypeError):
            SourceCodeParser()  # type: ignore

    def test_stub_parser_successfully_implements_interface(self) -> None:
        # 2. Stub parser successfully implements the interface
        parser = DummyParser()
        self.assertEqual(parser.parser_id, "dummy-parser-id")
        self.assertEqual(parser.language, Language.PYTHON)
        
        ast_result = parser.parse("print('test')")
        self.assertEqual(ast_result["ast"], "dummy-tree")
        self.assertEqual(ast_result["code"], "print('test')")

    def test_exception_hierarchy(self) -> None:
        # 3. Exception hierarchy
        self.assertTrue(issubclass(UnsupportedLanguageError, ParserError))
        self.assertTrue(issubclass(ParserInitializationError, ParserError))
        self.assertTrue(issubclass(ParseError, ParserError))

    def test_strong_typing_expectations(self) -> None:
        # 4. Strong typing expectations
        parser = DummyParser()
        with self.assertRaises(ParseError):
            parser.parse("")


if __name__ == "__main__":
    unittest.main()
