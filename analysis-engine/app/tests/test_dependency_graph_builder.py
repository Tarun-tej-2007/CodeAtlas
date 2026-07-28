"""Unit tests for the DependencyGraphBuilder class."""

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
from app.semantic.linking_pipeline import LinkedSemanticResult, ProjectSymbolIndex
from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_builder import DependencyGraphBuilder


class TestDependencyGraphBuilder(unittest.TestCase):
    """Tests dependency graph generation, imports/exports/usage edge mappings, and empty workspaces."""

    def setUp(self) -> None:
        self.builder = DependencyGraphBuilder()
        self.loc = Location(start_line=1, start_column=0, end_line=1, end_column=10)
        self.loc_a = SymbolLocation(file_path=Path("src/a.py"), location=self.loc)
        self.loc_b = SymbolLocation(file_path=Path("src/b.py"), location=self.loc)

        # Build some common test symbols
        self.sym_class = ProjectSymbol(
            id="sym-class-a",
            name="MyClass",
            qualified_name="src.a.MyClass",
            kind=SymbolKind.CLASS,
            location=self.loc_a,
        )

        self.sym_func = ProjectSymbol(
            id="sym-func-b",
            name="run",
            qualified_name="src.b.run",
            kind=SymbolKind.FUNCTION,
            location=self.loc_b,
        )

    def test_successful_graph_construction_and_edges(self) -> None:
        # File A exports MyClass, imports nothing
        exp_class = ExportDeclaration(exported_name="MyClass", local_symbol_id="sym-class-a", location=self.loc_a)
        file_a = ProjectFile(
            path=Path("src/a.py"),
            symbols=[self.sym_class],
            exports=[exp_class],
            imports=[],
            references=[]
        )

        # File B imports MyClass from a.py, defines run(), references MyClass
        imp_class = ImportDeclaration(imported_name="MyClass", module_specifier="./a", location=self.loc_b)
        ref_class = SymbolReference(name="MyClass", location=self.loc_b)
        file_b = ProjectFile(
            path=Path("src/b.py"),
            symbols=[self.sym_func],
            exports=[],
            imports=[imp_class],
            references=[ref_class]
        )

        project_result = ProjectSemanticResult(
            files={
                Path("src/a.py"): file_a,
                Path("src/b.py"): file_b
            }
        )

        # Mimic pipeline resolution results
        index = ProjectSymbolIndex(project_result.files)

        resolved_imp = ResolvedImport(
            import_declaration=imp_class,
            target_file=Path("src/a.py"),
            target_symbol=self.sym_class
        )
        import_export_res = ImportExportResolutionResult(
            resolved_imports=[resolved_imp],
            unresolved_imports=[],
            diagnostics=[]
        )

        resolved_ref = ResolvedReference(
            reference=ref_class,
            target_symbol=self.sym_class
        )
        ref_res = ReferenceResolutionResult(
            resolved_references=[resolved_ref],
            unresolved_references=[],
            diagnostics=[]
        )

        linked_result = LinkedSemanticResult(
            original_result=project_result,
            symbol_index=index,
            import_export_result=import_export_res,
            reference_resolution_result=ref_res,
            diagnostics=[]
        )

        # Build dependency graph
        graph = self.builder.build_graph(linked_result)

        # Verify Nodes
        self.assertTrue(graph.has_node("src/a.py"))
        self.assertTrue(graph.has_node("src/b.py"))
        self.assertTrue(graph.has_node("sym-class-a"))
        self.assertTrue(graph.has_node("sym-func-b"))

        # Verify Node Types
        self.assertEqual(graph.get_node("src/a.py").type, DependencyNodeType.MODULE)
        self.assertEqual(graph.get_node("sym-class-a").type, DependencyNodeType.CLASS)
        self.assertEqual(graph.get_node("sym-func-b").type, DependencyNodeType.FUNCTION)

        # Verify Edges
        # 1. IMPORTS edge: b.py -> a.py
        out_b = graph.get_outgoing_edges("src/b.py")
        import_edges = [e for e in out_b if e.type == DependencyEdgeType.IMPORTS]
        self.assertEqual(len(import_edges), 1)
        self.assertEqual(import_edges[0].target_id, "src/a.py")

        # 2. EXPORTS edge: a.py -> MyClass
        out_a = graph.get_outgoing_edges("src/a.py")
        export_edges = [e for e in out_a if e.type == DependencyEdgeType.EXPORTS]
        self.assertEqual(len(export_edges), 1)
        self.assertEqual(export_edges[0].target_id, "sym-class-a")

        # 3. USAGE edge: b.py -> MyClass (from reference resolution)
        usage_edges = [e for e in out_b if e.type == DependencyEdgeType.USAGE]
        self.assertEqual(len(usage_edges), 1)
        self.assertEqual(usage_edges[0].target_id, "sym-class-a")

        # Verify metadata
        self.assertEqual(graph.metadata.attributes["total_files"], 2)
        self.assertEqual(graph.metadata.attributes["total_nodes"], 4)

    def test_empty_and_single_file_project(self) -> None:
        # 1. Empty project
        empty_linked = LinkedSemanticResult(
            original_result=ProjectSemanticResult(files={}),
            symbol_index=ProjectSymbolIndex({}),
            import_export_result=ImportExportResolutionResult(),
            reference_resolution_result=ReferenceResolutionResult(),
            diagnostics=[]
        )
        graph_empty = self.builder.build_graph(empty_linked)
        self.assertEqual(len(graph_empty.nodes), 0)
        self.assertEqual(len(graph_empty.edges), 0)
        self.assertEqual(graph_empty.metadata.attributes["total_files"], 0)

        # 2. Single-file project
        file_a = ProjectFile(path=Path("src/a.py"), symbols=[self.sym_class])
        single_project = ProjectSemanticResult(files={Path("src/a.py"): file_a})
        single_linked = LinkedSemanticResult(
            original_result=single_project,
            symbol_index=ProjectSymbolIndex(single_project.files),
            import_export_result=ImportExportResolutionResult(),
            reference_resolution_result=ReferenceResolutionResult(),
            diagnostics=[]
        )
        graph_single = self.builder.build_graph(single_linked)
        self.assertEqual(len(graph_single.nodes), 2)  # module + sym-class-a
        self.assertEqual(len(graph_single.edges), 0)

    def test_duplicate_node_and_edge_protection(self) -> None:
        # If the input contains duplicate declarations or resolution maps, the builder
        # should handle it gracefully without crashing on duplicate exceptions
        clean_file_a = ProjectFile(path=Path("src/a.py"), symbols=[self.sym_class])
        clean_project = ProjectSemanticResult(files={Path("src/a.py"): clean_file_a})
        symbol_index = ProjectSymbolIndex(clean_project.files)

        duplicate_file_a = ProjectFile(
            path=Path("src/a.py"),
            symbols=[self.sym_class, self.sym_class],  # Duplicate symbol declaration
            exports=[]
        )
        project_result = ProjectSemanticResult(files={Path("src/a.py"): duplicate_file_a})

        # Reference resolved twice (duplicate edge usage)
        ref = SymbolReference(name="MyClass", location=self.loc_a)
        resolved_ref = ResolvedReference(reference=ref, target_symbol=self.sym_class)
        
        linked = LinkedSemanticResult(
            original_result=project_result,
            symbol_index=symbol_index,  # Pass valid ProjectSymbolIndex
            import_export_result=ImportExportResolutionResult(),
            reference_resolution_result=ReferenceResolutionResult(
                resolved_references=[resolved_ref, resolved_ref]  # Duplicate references
            ),
            diagnostics=[]
        )

        graph = self.builder.build_graph(linked)
        
        # Verify deduplication
        self.assertEqual(len(graph.nodes), 2)  # 1 module + 1 unique symbol
        self.assertEqual(len(graph.edges), 1)  # 1 unique usage edge

    def test_deterministic_and_immutable_outputs(self) -> None:
        file_a = ProjectFile(path=Path("src/a.py"), symbols=[self.sym_class])
        project_result = ProjectSemanticResult(files={Path("src/a.py"): file_a})
        linked = LinkedSemanticResult(
            original_result=project_result,
            symbol_index=ProjectSymbolIndex(project_result.files),
            import_export_result=ImportExportResolutionResult(),
            reference_resolution_result=ReferenceResolutionResult(),
            diagnostics=[]
        )

        graph1 = self.builder.build_graph(linked)
        graph2 = self.builder.build_graph(linked)

        # Output determinism
        self.assertEqual(graph1.nodes, graph2.nodes)
        self.assertEqual(graph1.edges, graph2.edges)


if __name__ == "__main__":
    unittest.main()
