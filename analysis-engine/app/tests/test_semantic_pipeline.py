"""Unit tests for the SemanticPipeline class."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock

from app.scanner.models import Language
from app.parser.models import ParseResult, ParsedFile
from app.semantic.enums import ScopeKind, SymbolKind, ReferenceKind
from app.semantic import (
    Location,
    SemanticSymbol,
    SemanticReference,
    ScopeNode,
    SemanticAnalysisContext,
    SemanticAnalysisPlugin,
    SemanticPipeline,
    TypeMetadataExtractor,
)


class DummyAnalysisPlugin(SemanticAnalysisPlugin):
    """A dummy plugin to track method call ordering and simulate symbol registration/reference resolution."""

    def __init__(self) -> None:
        self.call_order = []

    def build_scopes_and_symbols(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        self.call_order.append("build_scopes_and_symbols")
        
        # Define mock location
        loc = Location(start_line=1, start_column=0, end_line=1, end_column=5)

        # Register a class scope and a class symbol
        class_scope = context.scope_manager.create_scope(id="ClassA", kind=ScopeKind.CLASS, location=loc)
        sym = SemanticSymbol(
            id="sym-class-a",
            name="ClassA",
            qualified_name="global.ClassA",
            kind=SymbolKind.CLASS,
            language=Language.PYTHON,
            file_path=Path("main.py"),
            location=loc,
            scope_id="global",
        )
        context.symbol_table.register_symbol(sym)
        context.scope_manager.register_symbol("sym-class-a")

    def resolve_references(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        self.call_order.append("resolve_references")
        loc = Location(start_line=5, start_column=0, end_line=5, end_column=10)
        
        # Resolve reference to ClassA
        context.reference_resolver.resolve_reference(
            name="ClassA",
            location=loc,
            reference_kind=ReferenceKind.INSTANTIATE
        )

    def extract_type_metadata(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        self.call_order.append("extract_type_metadata")
        # Simulates checking context type extractor
        if context.type_extractor:
            context.diagnostics.append("Type extractor verified")


class FailingAnalysisPlugin(SemanticAnalysisPlugin):
    """A plugin designed to raise exceptions to verify pipeline fault recovery."""

    def build_scopes_and_symbols(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        raise ValueError("Database connection failure")

    def resolve_references(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        pass

    def extract_type_metadata(self, context: SemanticAnalysisContext, parse_result: ParseResult) -> None:
        pass


class TestSemanticPipeline(unittest.TestCase):
    """Tests the semantic pipeline orchestration passes, context generation, and fault recovery."""

    def setUp(self) -> None:
        # Mock parser pipeline input result
        self.parse_result = ParseResult(
            parsed_count=1,
            failed_count=0,
            files=[]
        )

    def test_pipeline_execution_order_and_aggregation(self) -> None:
        plugin = DummyAnalysisPlugin()
        extractor = MagicMock(spec=TypeMetadataExtractor)
        pipeline = SemanticPipeline(plugin=plugin, type_extractor=extractor)

        result = pipeline.execute(self.parse_result)

        # 1. Verify execution ordering
        self.assertEqual(plugin.call_order, [
            "build_scopes_and_symbols",
            "resolve_references",
            "extract_type_metadata"
        ])

        # 2. Verify result aggregation
        self.assertEqual(len(result.symbols), 1)
        self.assertEqual(result.symbols[0].id, "sym-class-a")

        self.assertEqual(len(result.references), 1)
        self.assertEqual(result.references[0].symbol_id, "sym-class-a")

        # 3. Verify scope nodes conversion to SemanticScope DTOs
        self.assertEqual(len(result.scopes), 2)  # global root scope and ClassA scope
        scope_ids = {s.id for s in result.scopes}
        self.assertEqual(scope_ids, {"global", "ClassA"})

        # Diagnostics verify type extractor run
        self.assertIn("Type extractor verified", result.diagnostics)

    def test_pipeline_stateless_repeated_executions(self) -> None:
        plugin = DummyAnalysisPlugin()
        pipeline = SemanticPipeline(plugin=plugin)

        result_1 = pipeline.execute(self.parse_result)
        result_2 = pipeline.execute(self.parse_result)

        # Confirm both results are separate and populated correctly
        self.assertEqual(len(result_1.symbols), 1)
        self.assertEqual(len(result_2.symbols), 1)

    def test_fault_propagation_diagnostics(self) -> None:
        plugin = FailingAnalysisPlugin()
        pipeline = SemanticPipeline(plugin=plugin)

        result = pipeline.execute(self.parse_result)

        # Verify execution failed gracefully and diagnostic error logged
        self.assertEqual(len(result.symbols), 0)
        self.assertEqual(len(result.diagnostics), 1)
        self.assertIn("Database connection failure", result.diagnostics[0])


if __name__ == "__main__":
    unittest.main()
