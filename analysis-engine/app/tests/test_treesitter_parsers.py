"""Unit tests for concrete Tree-sitter parsers and plugin integration."""

import unittest
import tree_sitter

from app.scanner.models import Language
from app.parser import (
    PythonParser,
    JavaScriptParser,
    TypeScriptParser,
    ParseError,
)
from app.plugins import (
    PythonPlugin,
    JavaScriptPlugin,
    TypeScriptPlugin,
)


class TestTreeSitterParsers(unittest.TestCase):
    """Verifies grammar loading, code parsing, and language plugin mappings."""

    def test_parser_identifiers(self) -> None:
        # 5. Parser identifiers
        py_parser = PythonParser()
        js_parser = JavaScriptParser()
        ts_parser = TypeScriptParser()

        self.assertEqual(py_parser.parser_id, "tree-sitter-python")
        self.assertEqual(js_parser.parser_id, "tree-sitter-javascript")
        self.assertEqual(ts_parser.parser_id, "tree-sitter-typescript")

    def test_language_reporting(self) -> None:
        # 6. Language reporting
        py_parser = PythonParser()
        js_parser = JavaScriptParser()
        ts_parser = TypeScriptParser()

        self.assertEqual(py_parser.language, Language.PYTHON)
        self.assertEqual(js_parser.language, Language.JAVASCRIPT)
        self.assertEqual(ts_parser.language, Language.TYPESCRIPT)

    def test_python_parsing(self) -> None:
        # 1. Python parser initialization & 4. Successful parsing of simple source snippets
        parser = PythonParser()
        code = "def hello():\n    print('world')"
        
        tree = parser.parse(code)
        self.assertIsInstance(tree, tree_sitter.Tree)
        self.assertIsNotNone(tree.root_node)
        self.assertEqual(tree.root_node.type, "module")

    def test_javascript_parsing(self) -> None:
        # 2. JavaScript parser initialization & 4. Successful parsing of simple source snippets
        parser = JavaScriptParser()
        code = "function hello() { console.log('world'); }"
        
        tree = parser.parse(code)
        self.assertIsInstance(tree, tree_sitter.Tree)
        self.assertIsNotNone(tree.root_node)
        self.assertEqual(tree.root_node.type, "program")

    def test_typescript_parsing(self) -> None:
        # 3. TypeScript parser initialization & 4. Successful parsing of simple source snippets
        parser = TypeScriptParser()
        code = "const val: number = 42;"
        
        tree = parser.parse(code)
        self.assertIsInstance(tree, tree_sitter.Tree)
        self.assertIsNotNone(tree.root_node)
        self.assertEqual(tree.root_node.type, "program")

    def test_exception_handling(self) -> None:
        # 7. Exception handling
        py_parser = PythonParser()
        
        # Test passing None value raising ParseError
        with self.assertRaises(ParseError):
            py_parser.parse(None)  # type: ignore

    def test_plugin_integration(self) -> None:
        # 8. Plugin integration
        py_plugin = PythonPlugin()
        js_plugin = JavaScriptPlugin()
        ts_plugin = TypeScriptPlugin()

        self.assertIsInstance(py_plugin.get_parser(), PythonParser)
        self.assertIsInstance(js_plugin.get_parser(), JavaScriptParser)
        self.assertIsInstance(ts_plugin.get_parser(), TypeScriptParser)

        # Confirm parser caching (returns the exact same instance on consecutive calls)
        self.assertIs(py_plugin.get_parser(), py_plugin.get_parser())
        self.assertIs(js_plugin.get_parser(), js_plugin.get_parser())
        self.assertIs(ts_plugin.get_parser(), ts_plugin.get_parser())


if __name__ == "__main__":
    unittest.main()
