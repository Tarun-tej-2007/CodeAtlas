"""Unit tests for CallGraphBuilder module."""

import unittest
from pathlib import Path

from app.semantic import SymbolKind
from app.semantic.project_models import (
    Location,
    SymbolLocation,
    ProjectSymbol,
    ImportDeclaration,
    ExportDeclaration,
    SymbolReference,
    ProjectFile,
    ProjectSemanticResult,
)
from app.semantic.import_export_resolver import (
    ResolvedImport,
    ImportExportResolutionResult,
)
from app.semantic.reference_resolver import (
    ResolvedReference,
    ReferenceResolutionResult,
)
from app.semantic.project_symbol_index import ProjectSymbolIndex
from app.semantic.linking_pipeline import LinkedSemanticResult
from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import DependencyMetadata, GraphEdge, GraphNode
from app.graph.dependency_graph import DependencyGraph
from app.graph.call_graph_builder import CallGraphBuilder


class TestCallGraphBuilder(unittest.TestCase):
    """Tests behavioral call graph builder mapping execution pathways."""

    def setUp(self) -> None:
        self.builder = CallGraphBuilder()

        # Coordinates
        self.loc_file = Path("src/main.py")
        
        # Enclosing Function caller_func spanning lines 10 to 20
        self.caller_func = ProjectSymbol(
            id="sym-caller-func",
            name="process",
            qualified_name="src.main.process",
            kind=SymbolKind.FUNCTION,
            location=SymbolLocation(
                file_path=self.loc_file,
                location=Location(start_line=10, start_column=0, end_line=20, end_column=10)
            )
        )

        # Function callee_func spanning lines 30 to 40
        self.callee_func = ProjectSymbol(
            id="sym-callee-func",
            name="compute",
            qualified_name="src.main.compute",
            kind=SymbolKind.FUNCTION,
            location=SymbolLocation(
                file_path=self.loc_file,
                location=Location(start_line=30, start_column=0, end_line=40, end_column=10)
            )
        )

        # Enclosing Method caller_method spanning lines 50 to 60
        self.caller_method = ProjectSymbol(
            id="sym-caller-method",
            name="MyClass.run",
            qualified_name="src.main.MyClass.run",
            kind=SymbolKind.METHOD,
            location=SymbolLocation(
                file_path=self.loc_file,
                location=Location(start_line=50, start_column=0, end_line=60, end_column=10)
            )
        )

        # Method callee_method spanning lines 70 to 80
        self.callee_method = ProjectSymbol(
            id="sym-callee-method",
            name="MyClass.save",
            qualified_name="src.main.MyClass.save",
            kind=SymbolKind.METHOD,
            location=SymbolLocation(
                file_path=self.loc_file,
                location=Location(start_line=70, start_column=0, end_line=80, end_column=10)
            )
        )

        # Node representation in base DependencyGraph
        self.nodes = [
            GraphNode(id=str(self.loc_file), name="main.py", type=DependencyNodeType.MODULE),
            GraphNode(id=self.caller_func.id, name="process", type=DependencyNodeType.FUNCTION),
            GraphNode(id=self.callee_func.id, name="compute", type=DependencyNodeType.FUNCTION),
            GraphNode(id=self.caller_method.id, name="MyClass.run", type=DependencyNodeType.METHOD),
            GraphNode(id=self.callee_method.id, name="MyClass.save", type=DependencyNodeType.METHOD),
        ]
        self.base_graph = DependencyGraph(
            nodes=self.nodes,
            edges=[],
            metadata=DependencyMetadata(description="Call base", version="1.0.0")
        )

        # Construct a reusable clean ProjectSymbolIndex to pass validation
        clean_project = ProjectSemanticResult(
            files={
                self.loc_file: ProjectFile(
                    path=self.loc_file,
                    symbols=[self.caller_func, self.callee_func, self.caller_method, self.callee_method]
                )
            }
        )
        self.symbol_index = ProjectSymbolIndex(clean_project.files)

    def test_function_to_function_calls(self) -> None:
        # A reference to "compute" at line 15 (inside caller_func)
        ref = SymbolReference(
            name="compute",
            location=SymbolLocation(
                file_path=self.loc_file,
                location=Location(start_line=15, start_column=4, end_line=15, end_column=11)
            )
        )
        resolved_ref = ResolvedReference(reference=ref, target_symbol=self.callee_func)
        
        project_file = ProjectFile(
            path=self.loc_file,
            symbols=[self.caller_func, self.callee_func],
            references=[ref]
        )
        linked = LinkedSemanticResult(
            original_result=ProjectSemanticResult(files={self.loc_file: project_file}),
            symbol_index=self.symbol_index,
            import_export_result=ImportExportResolutionResult(),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[resolved_ref]),
            diagnostics=[]
        )

        enriched = self.builder.build_call_graph(self.base_graph, linked)

        # Verify calls edge created: process -> compute
        calls_edges = enriched.get_outgoing_edges("sym-caller-func")
        self.assertEqual(len(calls_edges), 1)
        self.assertEqual(calls_edges[0].target_id, "sym-callee-func")
        self.assertEqual(calls_edges[0].type, DependencyEdgeType.CALLS)

    def test_method_to_method_and_mixed_calls(self) -> None:
        # 1. caller_method calls callee_method (method-to-method)
        ref1 = SymbolReference(
            name="save",
            location=SymbolLocation(
                file_path=self.loc_file,
                location=Location(start_line=55, start_column=4, end_line=55, end_column=8)
            )
        )
        resolved_ref1 = ResolvedReference(reference=ref1, target_symbol=self.callee_method)

        # 2. caller_func calls callee_method (function-to-method)
        ref2 = SymbolReference(
            name="save",
            location=SymbolLocation(
                file_path=self.loc_file,
                location=Location(start_line=18, start_column=4, end_line=18, end_column=8)
            )
        )
        resolved_ref2 = ResolvedReference(reference=ref2, target_symbol=self.callee_method)

        # 3. caller_method calls callee_func (method-to-function)
        ref3 = SymbolReference(
            name="compute",
            location=SymbolLocation(
                file_path=self.loc_file,
                location=Location(start_line=58, start_column=4, end_line=58, end_column=11)
            )
        )
        resolved_ref3 = ResolvedReference(reference=ref3, target_symbol=self.callee_func)

        project_file = ProjectFile(
            path=self.loc_file,
            symbols=[self.caller_func, self.caller_method, self.callee_method, self.callee_func],
            references=[ref1, ref2, ref3]
        )
        linked = LinkedSemanticResult(
            original_result=ProjectSemanticResult(files={self.loc_file: project_file}),
            symbol_index=self.symbol_index,
            import_export_result=ImportExportResolutionResult(),
            reference_resolution_result=ReferenceResolutionResult(
                resolved_references=[resolved_ref1, resolved_ref2, resolved_ref3]
            ),
            diagnostics=[]
        )

        enriched = self.builder.build_call_graph(self.base_graph, linked)

        # Check sym-caller-method outgoing edges
        out_method = enriched.get_outgoing_edges("sym-caller-method")
        self.assertEqual(len(out_method), 2)
        targets = {e.target_id for e in out_method}
        self.assertEqual(targets, {"sym-callee-method", "sym-callee-func"})

        # Check sym-caller-func outgoing edges
        out_func = enriched.get_outgoing_edges("sym-caller-func")
        self.assertEqual(len(out_func), 1)
        self.assertEqual(out_func[0].target_id, "sym-callee-method")

    def test_recursive_calls(self) -> None:
        # caller_func calls caller_func
        ref = SymbolReference(
            name="process",
            location=SymbolLocation(
                file_path=self.loc_file,
                location=Location(start_line=15, start_column=4, end_line=15, end_column=11)
            )
        )
        resolved_ref = ResolvedReference(reference=ref, target_symbol=self.caller_func)

        project_file = ProjectFile(path=self.loc_file, symbols=[self.caller_func], references=[ref])
        linked = LinkedSemanticResult(
            original_result=ProjectSemanticResult(files={self.loc_file: project_file}),
            symbol_index=self.symbol_index,
            import_export_result=ImportExportResolutionResult(),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[resolved_ref]),
            diagnostics=[]
        )

        enriched = self.builder.build_call_graph(self.base_graph, linked)

        calls = enriched.get_outgoing_edges("sym-caller-func")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].target_id, "sym-caller-func")

    def test_duplicate_call_elimination(self) -> None:
        # caller_func calls callee_func twice
        ref1 = SymbolReference(
            name="compute",
            location=SymbolLocation(
                file_path=self.loc_file,
                location=Location(start_line=12, start_column=4, end_line=12, end_column=11)
            )
        )
        ref2 = SymbolReference(
            name="compute",
            location=SymbolLocation(
                file_path=self.loc_file,
                location=Location(start_line=16, start_column=4, end_line=16, end_column=11)
            )
        )
        resolved_ref1 = ResolvedReference(reference=ref1, target_symbol=self.callee_func)
        resolved_ref2 = ResolvedReference(reference=ref2, target_symbol=self.callee_func)

        project_file = ProjectFile(
            path=self.loc_file,
            symbols=[self.caller_func, self.callee_func],
            references=[ref1, ref2]
        )
        linked = LinkedSemanticResult(
            original_result=ProjectSemanticResult(files={self.loc_file: project_file}),
            symbol_index=self.symbol_index,
            import_export_result=ImportExportResolutionResult(),
            reference_resolution_result=ReferenceResolutionResult(
                resolved_references=[resolved_ref1, resolved_ref2]
            ),
            diagnostics=[]
        )

        enriched = self.builder.build_call_graph(self.base_graph, linked)

        # Output edge count must be 1 due to deduplication
        calls = enriched.get_outgoing_edges("sym-caller-func")
        self.assertEqual(len(calls), 1)

    def test_project_without_calls(self) -> None:
        empty_index = ProjectSymbolIndex({})
        linked = LinkedSemanticResult(
            original_result=ProjectSemanticResult(files={}),
            symbol_index=empty_index,
            import_export_result=ImportExportResolutionResult(),
            reference_resolution_result=ReferenceResolutionResult(),
            diagnostics=[]
        )

        enriched = self.builder.build_call_graph(self.base_graph, linked)
        self.assertEqual(len(enriched.edges), 0)


if __name__ == "__main__":
    unittest.main()
