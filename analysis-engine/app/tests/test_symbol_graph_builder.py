"""Unit test suite for SymbolGraphBuilder structural graph construction."""

from pathlib import Path
import unittest

from app.analyzer import AnalysisContext
from app.graph import (
    EdgeType,
    Graph,
    GraphBuilderError,
    NodeType,
    SymbolGraphBuilder,
)
from app.parser import Language, ParsedFile, TreeSitterParser
from app.parser.ast import ASTBuilder
from app.parser.modules import ModuleAnalyzer
from app.parser.symbols import SymbolExtractor


class TestSymbolGraphBuilder(unittest.TestCase):
    """Tests for SymbolGraphBuilder node and edge creation, nesting, and duplicate prevention."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.symbol_extractor = SymbolExtractor()
        self.module_analyzer = ModuleAnalyzer()
        self.graph_builder = SymbolGraphBuilder(project_name="TestProject")
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

    def test_single_file_symbol_graph(self) -> None:
        code = """
        function calculate() { return 42; }
        const secret = 10;
        """
        ctx = self._create_context(code, Language.JAVASCRIPT, "single.js")
        graph = self.graph_builder.build(ctx)

        self.assertIsInstance(graph, Graph)
        self.assertEqual(graph.metadata.project_name, "TestProject")

        # Must have PROJECT, FILE, and 2 Symbol nodes
        self.assertEqual(graph.node_count(), 4)
        node_types = {n.type for n in graph.nodes}
        self.assertIn(NodeType.PROJECT, node_types)
        self.assertIn(NodeType.FILE, node_types)
        self.assertIn(NodeType.FUNCTION, node_types)
        self.assertIn(NodeType.VARIABLE, node_types)

        # Must have CONTAINS edge (PROJECT -> FILE) and DECLARES edges (FILE -> Symbol)
        self.assertEqual(graph.edge_count(), 3)
        contains_edges = graph.get_edges(edge_type=EdgeType.CONTAINS)
        self.assertEqual(len(contains_edges), 1)

        declares_edges = graph.get_edges(edge_type=EdgeType.DECLARES)
        self.assertEqual(len(declares_edges), 2)

    def test_classes_interfaces_enums_nested_declarations(self) -> None:
        code = """
        export interface UserConfig {
            theme: string;
        }

        export enum Role {
            ADMIN,
            USER
        }

        export class UserService {
            getUser() {
                const innerVar = 1;
            }
        }
        """
        ctx = self._create_context(code, Language.TYPESCRIPT, "service.ts")
        graph = self.graph_builder.build(ctx)

        node_types = {n.type for n in graph.nodes}
        self.assertIn(NodeType.INTERFACE, node_types)
        self.assertIn(NodeType.ENUM, node_types)
        self.assertIn(NodeType.CLASS, node_types)
        self.assertIn(NodeType.METHOD, node_types)

        # Check nested method edge
        method_nodes = [n for n in graph.nodes if n.type == NodeType.METHOD]
        self.assertEqual(len(method_nodes), 1)
        method_id = method_nodes[0].id

        class_nodes = [n for n in graph.nodes if n.type == NodeType.CLASS]
        class_id = class_nodes[0].id

        class_method_edges = graph.get_edges(source_id=class_id, target_id=method_id)
        self.assertEqual(len(class_method_edges), 1)

    def test_multiple_files_symbol_graph(self) -> None:
        ctx1 = self._create_context("function f1() {}", Language.JAVASCRIPT, "mod1.js")
        ctx2 = self._create_context("function f2() {}", Language.JAVASCRIPT, "mod2.js")

        graph = self.graph_builder.build([ctx1, ctx2])

        file_nodes = [n for n in graph.nodes if n.type == NodeType.FILE]
        self.assertEqual(len(file_nodes), 2)

        contains_edges = graph.get_edges(edge_type=EdgeType.CONTAINS)
        self.assertEqual(len(contains_edges), 2)

    def test_duplicate_prevention_on_repeated_context(self) -> None:
        ctx = self._create_context("function test() {}", Language.JAVASCRIPT, "app.js")
        graph1 = self.graph_builder.build(ctx)
        graph2 = self.graph_builder.build([ctx, ctx])

        self.assertEqual(graph1.node_count(), graph2.node_count())
        self.assertEqual(graph1.edge_count(), graph2.edge_count())

    def test_invalid_context_raises_builder_error(self) -> None:
        with self.assertRaises(GraphBuilderError):
            self.graph_builder.build(None)  # type: ignore


if __name__ == "__main__":
    unittest.main()
