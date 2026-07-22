"""Hardening and refinements unit tests for the parsing subsystem."""

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock

from app.scanner.models import DiscoveredFile, Language as ScannerLanguage
from app.parser.models import ParsedFile, ParseResult
from app.parser.exceptions import ParseError, ParserInitializationError
from app.parser.base import SourceCodeParser
from app.plugins import PluginRegistry, PythonPlugin, JavaScriptPlugin, TypeScriptPlugin
from app.plugins.exceptions import PluginNotFoundError
from app.parser import ParsingPipeline


class TestParserRefinements(unittest.TestCase):
    """Verifies edge case recovery, partial failures, and performance behaviors in parsing pipeline."""

    def setUp(self) -> None:
        self.temp_dir = tempfile.mkdtemp()
        self.registry = PluginRegistry()
        self.pipeline = ParsingPipeline(registry=self.registry)

    def tearDown(self) -> None:
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_malformed_syntax_source_parsed_with_error_nodes(self) -> None:
        # Malformed source files: Tree-sitter error recovery allows parsing to succeed with error nodes
        # Python plugin setup
        self.registry.register(PythonPlugin())
        
        file_path = Path(self.temp_dir) / "malformed.py"
        # Invalid python syntax (unmatched parenthesis)
        file_path.write_text("def unmatched_paren(\n    print('hello'")

        discovered = DiscoveredFile(
            absolute_path=file_path,
            relative_path=Path("malformed.py"),
            extension=".py",
            size=file_path.stat().st_size,
            language=ScannerLanguage.PYTHON,
        )

        result = self.pipeline.parse_files([discovered])

        # Assert: parsing itself does not fail because tree-sitter recovers and returns a Tree
        self.assertEqual(result.parsed_count, 1)
        self.assertEqual(result.failed_count, 0)
        self.assertEqual(len(result.files), 1)
        
        # Check that the tree root node is valid but contains errors (tree-sitter specific check)
        tree = result.files[0].tree
        self.assertIsNotNone(tree)
        self.assertTrue(tree.root_node.has_error)

    def test_parser_initialization_failure_recovery(self) -> None:
        # Parser initialization failures: one plugin fails to return a parser, pipeline recovers
        mock_plugin = MagicMock()
        mock_plugin.language = ScannerLanguage.PYTHON
        mock_plugin.get_parser.side_effect = ParserInitializationError("Failed to init grammars")

        self.registry.register(mock_plugin)

        file_path = Path(self.temp_dir) / "test.py"
        file_path.write_text("print(1)")

        discovered = DiscoveredFile(
            absolute_path=file_path,
            relative_path=Path("test.py"),
            extension=".py",
            size=file_path.stat().st_size,
            language=ScannerLanguage.PYTHON,
        )

        result = self.pipeline.parse_files([discovered])

        # Assert that initialization error was handled and added to failed_count
        self.assertEqual(result.parsed_count, 0)
        self.assertEqual(result.failed_count, 1)

    def test_parse_error_recovery_during_execution(self) -> None:
        # Partial parsing failures: parse() method raises ParseError
        mock_parser = MagicMock(spec=SourceCodeParser)
        mock_parser.parse.side_effect = ParseError("Parsing crashed")

        mock_plugin = MagicMock()
        mock_plugin.language = ScannerLanguage.PYTHON
        mock_plugin.get_parser.return_value = mock_parser

        self.registry.register(mock_plugin)

        file_path = Path(self.temp_dir) / "test.py"
        file_path.write_text("print(1)")

        discovered = DiscoveredFile(
            absolute_path=file_path,
            relative_path=Path("test.py"),
            extension=".py",
            size=file_path.stat().st_size,
            language=ScannerLanguage.PYTHON,
        )

        result = self.pipeline.parse_files([discovered])

        # Assert ParseError was handled and added to failed_count
        self.assertEqual(result.parsed_count, 0)
        self.assertEqual(result.failed_count, 1)

    def test_parser_reuse_efficiency(self) -> None:
        # Parser reuse: Verify that calling get_parser multiple times returns cached parser instances
        py_plugin = PythonPlugin()
        parser1 = py_plugin.get_parser()
        parser2 = py_plugin.get_parser()
        self.assertIs(parser1, parser2)


if __name__ == "__main__":
    unittest.main()
