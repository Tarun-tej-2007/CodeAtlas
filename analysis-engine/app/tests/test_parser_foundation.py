"""Unit test suite for the parser domain foundation."""

from pathlib import Path
import unittest
import tree_sitter

from app.parser import (
    BaseParser,
    Language,
    ParsedFile,
    ParseFailureError,

    ParseResult,
    ParserError,
    ParserInitializationError,
    ParserRegistry,
    UnsupportedLanguageError,
    create_treesitter_parser,
)


class DummyTestParser(BaseParser):
    """Concrete dummy implementation of BaseParser for registry testing."""

    def parse_file(self, file_path: Path, repository_root: Path) -> ParsedFile:
        return ParsedFile(
            path=file_path,
            relative_path=file_path.relative_to(repository_root),
            language=Language.JAVASCRIPT,
            source_code="console.log('dummy');",
            tree=None,
        )


class TestParserFoundation(unittest.TestCase):
    """Tests for parser domain models, language enum, exceptions, registry, and Tree-sitter init."""

    def test_language_enum_and_from_str(self):
        self.assertEqual(Language.JAVASCRIPT, "javascript")
        self.assertEqual(Language.TYPESCRIPT, "typescript")

        self.assertEqual(Language.from_str("JavaScript"), Language.JAVASCRIPT)
        self.assertEqual(Language.from_str("js"), Language.JAVASCRIPT)
        self.assertEqual(Language.from_str(".jsx"), Language.JAVASCRIPT)
        self.assertEqual(Language.from_str("TypeScript"), Language.TYPESCRIPT)
        self.assertEqual(Language.from_str(".ts"), Language.TYPESCRIPT)
        self.assertEqual(Language.from_str(".tsx"), Language.TYPESCRIPT)

        with self.assertRaises(UnsupportedLanguageError):
            Language.from_str("python")

    def test_exception_hierarchy(self):
        self.assertTrue(issubclass(UnsupportedLanguageError, ParserError))
        self.assertTrue(issubclass(ParserInitializationError, ParserError))
        self.assertTrue(issubclass(ParseFailureError, ParserError))

    def test_parsed_file_model_and_immutability(self):
        ts_parser = create_treesitter_parser(Language.JAVASCRIPT)
        tree = ts_parser.parse(b"const x = 1;")

        parsed = ParsedFile(
            path=Path("/repo/app.js"),
            relative_path=Path("app.js"),
            language=Language.JAVASCRIPT,
            source_code="const x = 1;",
            tree=tree,
        )

        self.assertEqual(parsed.filename if hasattr(parsed, 'filename') else parsed.path.name, "app.js")
        self.assertEqual(parsed.language, Language.JAVASCRIPT)
        self.assertEqual(parsed.tree.root_node.type, "program")

        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            parsed.source_code = "modified"

    def test_parse_result_statistics_defaults(self):
        res = ParseResult()
        self.assertEqual(res.parsed_count, 0)
        self.assertEqual(res.failed_count, 0)
        self.assertEqual(res.parse_duration_ms, 0.0)
        self.assertEqual(len(res.files), 0)

    def test_treesitter_parser_initialization(self):
        js_parser = create_treesitter_parser(Language.JAVASCRIPT)
        self.assertIsInstance(js_parser, tree_sitter.Parser)

        ts_parser = create_treesitter_parser(Language.TYPESCRIPT)
        self.assertIsInstance(ts_parser, tree_sitter.Parser)

        with self.assertRaises(UnsupportedLanguageError):
            create_treesitter_parser("ruby")  # type: ignore

    def test_parser_registry_workflow(self):
        registry = ParserRegistry()
        self.assertEqual(len(registry.supported_languages()), 0)

        dummy = DummyTestParser()
        registry.register(Language.JAVASCRIPT, dummy)

        self.assertIn(Language.JAVASCRIPT, registry.supported_languages())
        fetched = registry.get(Language.JAVASCRIPT)
        self.assertEqual(fetched, dummy)

        with self.assertRaises(UnsupportedLanguageError):
            registry.get(Language.TYPESCRIPT)

        registry.clear()
        self.assertEqual(len(registry.supported_languages()), 0)


if __name__ == "__main__":
    unittest.main()
