"""Unit test suite for CallGraphBuilder call graph enrichment."""

from pathlib import Path
import unittest

from app.analyzer import AnalysisContext
from app.analyzer.calls import CallAnalyzer, CallKind
from app.analyzer.resolution import SymbolResolver
from app.graph import (
    CallGraphBuilder,
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


class TestCallGraphBuilder(unittest.TestCase):
    """Tests for CallGraphBuilder CALLS edge generation, caller tracking, and unresolved call filtering."""

    def setUp(self) -> None:
        self.builder = ASTBuilder()
        self.symbol_extractor = SymbolExtractor()
        self.module_analyzer = ModuleAnalyzer()
        self.resolver = SymbolResolver()
        self.call_analyzer = CallAnalyzer()
        self.symbol_graph_builder = SymbolGraphBuilder(project_name="CallTestProject")
        self.call_graph_builder = CallGraphBuilder()
        self.js_parser = TreeSitterParser(Language.JAVASCRIPT)

    def _create_context(self, code: str, filename: str = "app.js") -> AnalysisContext:
        file_path = Path(f"/repo/{filename}")
        parsed = ParsedFile(
            path=file_path,
            relative_path=Path(filename),
            language=Language.JAVASCRIPT,
            source_code=code,
            tree=self.js_parser._ts_parser.parse(code.encode("utf-8")),
        )
        ast_doc = self.builder.build_document(parsed)
        symbols = self.symbol_extractor.extract(ast_doc)
        modules = self.module_analyzer.analyze(ast_doc)
        return AnalysisContext(
            ast_document=ast_doc,
            symbol_table=symbols,
            module_metadata=modules,
        )

    def test_function_method_constructor_static_calls(self) -> None:
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
        ctx = self._create_context(code, "main.js")
        res = self.resolver.resolve(ctx)
        call_res = self.call_analyzer.analyze(ctx, res)

        graph = self.symbol_graph_builder.build(ctx)
        initial_edge_count = graph.edge_count()

        # Enrich graph with CALLS edges
        enriched_graph = self.call_graph_builder.build(graph, ctx, call_res)

        self.assertGreater(enriched_graph.edge_count(), initial_edge_count)
        call_edges = enriched_graph.get_edges(edge_type=EdgeType.CALLS)
        self.assertGreaterEqual(len(call_edges), 4)

        kinds = {e.metadata["kind"] for e in call_edges}
        self.assertIn(CallKind.FUNCTION.value, kinds)
        self.assertIn(CallKind.CONSTRUCTOR.value, kinds)
        self.assertIn(CallKind.METHOD.value, kinds)
        self.assertIn(CallKind.STATIC_METHOD.value, kinds)

    def test_recursive_calls_enrichment(self) -> None:
        code = """
        function factorial(n) {
            if (n <= 1) return 1;
            return n * factorial(n - 1);
        }
        """
        ctx = self._create_context(code, "rec.js")
        res = self.resolver.resolve(ctx)
        call_res = self.call_analyzer.analyze(ctx, res)

        graph = self.symbol_graph_builder.build(ctx)
        enriched = self.call_graph_builder.build(graph, ctx, call_res)

        call_edges = enriched.get_edges(edge_type=EdgeType.CALLS)
        self.assertEqual(len(call_edges), 1)
        self.assertEqual(call_edges[0].source, call_edges[0].target)

    def test_unresolved_calls_ignored(self) -> None:
        code = "function test() { unknownFunction(); }"
        ctx = self._create_context(code, "unresolved.js")
        res = self.resolver.resolve(ctx)
        call_res = self.call_analyzer.analyze(ctx, res)

        graph = self.symbol_graph_builder.build(ctx)
        enriched = self.call_graph_builder.build(graph, ctx, call_res)

        call_edges = enriched.get_edges(edge_type=EdgeType.CALLS)
        self.assertEqual(len(call_edges), 0)

    def test_duplicate_edge_prevention(self) -> None:
        code = "function calc() {} function main() { calc(); }"
        ctx = self._create_context(code, "dup.js")
        res = self.resolver.resolve(ctx)
        call_res = self.call_analyzer.analyze(ctx, res)

        graph = self.symbol_graph_builder.build(ctx)
        self.call_graph_builder.build(graph, ctx, call_res)
        first_count = graph.edge_count()

        # Re-enriching should not add duplicate edges
        self.call_graph_builder.build(graph, ctx, call_res)
        second_count = graph.edge_count()

        self.assertEqual(first_count, second_count)

    def test_invalid_graph_raises_builder_error(self) -> None:
        with self.assertRaises(GraphBuilderError):
            self.call_graph_builder.build(None)  # type: ignore


if __name__ == "__main__":
    unittest.main()
