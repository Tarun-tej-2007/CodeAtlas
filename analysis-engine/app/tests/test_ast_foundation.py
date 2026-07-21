"""Unit test suite for normalized AST models, ASTBuilder, and ASTVisitor."""

from pathlib import Path
import unittest

from app.parser import (
    Language,
    ParsedFile,
    TreeSitterParser,
)
from app.parser.ast import (
    ASTBuilder,
    ASTBuilderError,
    ASTDocument,
    ASTError,
    ASTNode,
    ASTVisitor,
)


class NodeCollectorVisitor(ASTVisitor):
    """Test helper visitor that collects all visited ASTNodes in sequence."""

    def __init__(self) -> None:
        self.visited_nodes: list[ASTNode] = []

    def visit_node(self, node: ASTNode) -> None:
        self.visited_nodes.append(node)


class TestASTFoundation(unittest.TestCase):
    """Tests for normalized AST models, ASTBuilder, ASTVisitor, and error handling."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.js_parser = TreeSitterParser(Language.JAVASCRIPT)
        self.ts_parser = TreeSitterParser(Language.TYPESCRIPT)

    def test_ast_node_and_document_immutability(self) -> None:
        root_node = ASTNode(
            id="ast_1_0_1_12_program_0",
            type="program",
            text="const a = 1;",
            start_line=1,
            start_column=0,
            end_line=1,
            end_column=12,
            children=[],
        )
        doc = ASTDocument(
            path=Path("/repo/app.js"),
            relative_path=Path("app.js"),
            language=Language.JAVASCRIPT,
            root=root_node,
        )

        self.assertEqual(doc.root.type, "program")
        self.assertEqual(doc.root.start_line, 1)

        from pydantic import ValidationError
        with self.assertRaises(ValidationError):
            doc.root.type = "modified"

        with self.assertRaises(ValidationError):
            doc.language = Language.TYPESCRIPT

    def test_build_ast_from_javascript_source(self) -> None:
        file_path = Path("/repo/main.js")
        js_code = "function sum(a, b) { return a + b; }"

        mock_parsed = ParsedFile(
            path=file_path,
            relative_path=Path("main.js"),
            language=Language.JAVASCRIPT,
            source_code=js_code,
            tree=self.js_parser._ts_parser.parse(js_code.encode("utf-8")),
        )

        doc = self.builder.build_document(mock_parsed)
        self.assertEqual(doc.path, file_path)
        self.assertEqual(doc.language, Language.JAVASCRIPT)
        self.assertEqual(doc.root.type, "program")
        self.assertGreater(len(doc.root.children), 0)

        # Check function_declaration child node
        fn_node = doc.root.children[0]
        self.assertIn("function", fn_node.text)

    def test_build_ast_from_typescript_source(self) -> None:
        file_path = Path("/repo/types.ts")
        repo_root = Path("/repo")
        ts_code = "export interface User { id: number; name: string; }"

        mock_parsed = ParsedFile(
            path=file_path,
            relative_path=Path("types.ts"),
            language=Language.TYPESCRIPT,
            source_code=ts_code,
            tree=self.ts_parser._ts_parser.parse(ts_code.encode("utf-8")),
        )

        doc = self.builder.build_document(mock_parsed)
        self.assertEqual(doc.language, Language.TYPESCRIPT)
        self.assertEqual(doc.root.type, "program")

    def test_empty_program_ast(self) -> None:
        file_path = Path("/repo/empty.js")
        mock_parsed = ParsedFile(
            path=file_path,
            relative_path=Path("empty.js"),
            language=Language.JAVASCRIPT,
            source_code="",
            tree=self.js_parser._ts_parser.parse(b""),
        )

        doc = self.builder.build_document(mock_parsed)
        self.assertEqual(doc.root.type, "program")
        self.assertEqual(doc.root.text, "")
        self.assertEqual(len(doc.root.children), 0)

    def test_ast_visitor_depth_first_traversal(self) -> None:
        js_code = "const x = 5; const y = 10;"
        mock_parsed = ParsedFile(
            path=Path("/repo/var.js"),
            relative_path=Path("var.js"),
            language=Language.JAVASCRIPT,
            source_code=js_code,
            tree=self.js_parser._ts_parser.parse(js_code.encode("utf-8")),
        )

        doc = self.builder.build_document(mock_parsed)

        collector = NodeCollectorVisitor()
        collector.visit(doc.root)

        self.assertGreater(len(collector.visited_nodes), 1)
        self.assertEqual(collector.visited_nodes[0].type, "program")

    def test_deterministic_node_ids_and_ordering(self) -> None:
        js_code = "let item = 'codeatlas';"
        tree1 = self.js_parser._ts_parser.parse(js_code.encode("utf-8"))
        tree2 = self.js_parser._ts_parser.parse(js_code.encode("utf-8"))

        p1 = ParsedFile(
            path=Path("/repo/a.js"),
            relative_path=Path("a.js"),
            language=Language.JAVASCRIPT,
            source_code=js_code,
            tree=tree1,
        )
        p2 = ParsedFile(
            path=Path("/repo/a.js"),
            relative_path=Path("a.js"),
            language=Language.JAVASCRIPT,
            source_code=js_code,
            tree=tree2,
        )

        doc1 = self.builder.build_document(p1)
        doc2 = self.builder.build_document(p2)

        self.assertEqual(doc1.root.model_dump(), doc2.root.model_dump())

    def test_builder_error_handling(self) -> None:
        p_invalid = ParsedFile(
            path=Path("/repo/bad.js"),
            relative_path=Path("bad.js"),
            language=Language.JAVASCRIPT,
            source_code="",
            tree=None,
        )

        with self.assertRaises(ASTBuilderError):
            self.builder.build_document(p_invalid)

        self.assertTrue(issubclass(ASTBuilderError, ASTError))


if __name__ == "__main__":
    unittest.main()
