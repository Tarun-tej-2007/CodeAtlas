"""Comprehensive integration and validation tests for the entire graph subsystem."""

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
from app.graph.dependency_models import GraphNode, GraphEdge, DependencyMetadata
from app.graph.exceptions import (
    DuplicateEdgeError,
    DuplicateNodeError,
    GraphValidationError,
)
from app.graph import (
    DependencyGraph,
    DependencyGraphBuilder,
    CallGraphBuilder,
    CycleDetector,
    SCCEngine,
    DependencyGraphQuery,
)


class TestGraphValidationIntegration(unittest.TestCase):
    """Exercises the complete graph lifecycle, diagnostics invariants, and exception paths."""

    def setUp(self) -> None:
        self.dep_builder = DependencyGraphBuilder()
        self.call_builder = CallGraphBuilder()
        self.cycle_detector = CycleDetector()
        self.scc_engine = SCCEngine()
        self.query = DependencyGraphQuery()

        self.loc = Location(start_line=1, start_column=0, end_line=5, end_column=10)
        self.loc_file = Path("src/app.py")

        self.sym_main = ProjectSymbol(
            id="sym-main",
            name="main",
            qualified_name="src.app.main",
            kind=SymbolKind.FUNCTION,
            location=SymbolLocation(file_path=self.loc_file, location=self.loc),
        )

    def test_end_to_end_graph_pipeline(self) -> None:
        # File imports a module, exports main(), calls main() recursively
        imp = ImportDeclaration(imported_name="utils", module_specifier="./utils", location=SymbolLocation(file_path=self.loc_file, location=self.loc))
        exp = ExportDeclaration(exported_name="main", local_symbol_id="sym-main", location=SymbolLocation(file_path=self.loc_file, location=self.loc))
        ref = SymbolReference(name="main", location=SymbolLocation(file_path=self.loc_file, location=Location(start_line=2, start_column=4, end_line=2, end_column=8)))
        
        file_obj = ProjectFile(
            path=self.loc_file,
            symbols=[self.sym_main],
            imports=[imp],
            exports=[exp],
            references=[ref]
        )
        file_utils = ProjectFile(
            path=Path("src/utils.py"),
            symbols=[],
            imports=[],
            exports=[],
            references=[]
        )

        project_result = ProjectSemanticResult(
            files={
                self.loc_file: file_obj,
                Path("src/utils.py"): file_utils
            }
        )
        symbol_index = ProjectSymbolIndex(project_result.files)

        resolved_imp = ResolvedImport(
            import_declaration=imp,
            target_file=Path("src/utils.py"),
            target_symbol=self.sym_main
        )
        import_res = ImportExportResolutionResult(resolved_imports=[resolved_imp])

        resolved_ref = ResolvedReference(reference=ref, target_symbol=self.sym_main)
        ref_res = ReferenceResolutionResult(resolved_references=[resolved_ref])

        linked = LinkedSemanticResult(
            original_result=project_result,
            symbol_index=symbol_index,
            import_export_result=import_res,
            reference_resolution_result=ref_res,
            diagnostics=[]
        )

        # 1. Build Structural Dependency Graph
        dep_graph = self.dep_builder.build_graph(linked)
        self.assertEqual(len(dep_graph.nodes), 3) # src/app.py, sym-main, src/utils.py
        self.assertEqual(len(dep_graph.edges), 3) # IMPORTS: app -> utils, EXPORTS: app -> sym-main, USAGE: app -> sym-main

        # 2. Enrich with CALLS edges
        full_graph = self.call_builder.build_call_graph(dep_graph, linked)
        self.assertEqual(len(full_graph.edges), 4) # IMPORTS, EXPORTS, USAGE + CALLS: sym-main -> sym-main (recursive)

        # 3. Detect Cycles
        cycles = self.cycle_detector.detect_cycles(full_graph)
        self.assertEqual(cycles.cycles, [["sym-main", "sym-main"]])

        # 4. Compute SCCs
        sccs = self.scc_engine.compute_scc(full_graph)
        # 3 nodes: src/app.py (scc), src/utils.py (scc), sym-main (scc)
        self.assertEqual(len(sccs.components), 3)

        # 5. Queries & traversals
        neighbours = self.query.get_neighbours(full_graph, str(self.loc_file))
        neighbour_ids = [n.id for n in neighbours]
        self.assertEqual(sorted(neighbour_ids), ["src/utils.py", "sym-main"])

    def test_malformed_input_validation(self) -> None:
        # Duplicate node ID validation
        node1 = GraphNode(id="node-a", name="A", type=DependencyNodeType.MODULE)
        node2 = GraphNode(id="node-a", name="A_dup", type=DependencyNodeType.MODULE)
        with self.assertRaises(DuplicateNodeError):
            DependencyGraph(nodes=[node1, node2], edges=[])

        # Edge referencing non-existent nodes
        edge = GraphEdge(source_id="node-a", target_id="node-ghost", type=DependencyEdgeType.USAGE)
        
        with self.assertRaises(GraphValidationError):
            DependencyGraph(nodes=[node1], edges=[edge])

    def test_repeated_deterministic_execution(self) -> None:
        # Ensure that repeated runs over the same graph produce identical, immutable components
        node_a = GraphNode(id="node-a", name="A", type=DependencyNodeType.MODULE)
        node_b = GraphNode(id="node-b", name="B", type=DependencyNodeType.MODULE)
        edge_ab = GraphEdge(source_id="node-a", target_id="node-b", type=DependencyEdgeType.IMPORTS)
        edge_ba = GraphEdge(source_id="node-b", target_id="node-a", type=DependencyEdgeType.IMPORTS)

        graph = DependencyGraph(nodes=[node_a, node_b], edges=[edge_ab, edge_ba])

        cycles1 = self.cycle_detector.detect_cycles(graph)
        cycles2 = self.cycle_detector.detect_cycles(graph)
        self.assertEqual(cycles1.cycles, cycles2.cycles)

        scc1 = self.scc_engine.compute_scc(graph)
        scc2 = self.scc_engine.compute_scc(graph)
        self.assertEqual(scc1.components, scc2.components)


if __name__ == "__main__":
    unittest.main()
