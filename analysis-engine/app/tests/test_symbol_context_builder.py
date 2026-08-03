"""Unit tests for the Symbol Context Builder."""

import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import GraphNode, GraphEdge
from app.graph.dependency_graph import DependencyGraph

from app.semantic.enums import SymbolKind, VisibilityKind
from app.semantic.models import Location
from app.semantic.project_models import ProjectSemanticResult, ProjectFile, ProjectSymbol, SymbolLocation, ImportDeclaration, ExportDeclaration
from app.semantic.linking_pipeline import LinkedSemanticResult
from app.semantic.project_symbol_index import ProjectSymbolIndex
from app.semantic.import_export_resolver import ImportExportResolutionResult, ResolvedImport
from app.semantic.reference_resolver import ReferenceResolutionResult

from app.architecture.enums import LayerType, SeverityLevel, AnalysisCategory
from app.architecture.models import ArchitectureLayer, ArchitectureIssue, ArchitectureAnalysisResult

from app.ai import SymbolContextBuilder, ContextPriority, ContextType


class TestSymbolContextBuilder(unittest.TestCase):
    """Verifies symbol context metadata extraction, call graph resolution, and concurrent safety."""

    def setUp(self) -> None:
        self.builder = SymbolContextBuilder()
        self.dummy_loc = SymbolLocation(
            file_path=Path("src/math.py"),
            location=Location(start_line=5, start_column=4, end_line=8, end_column=0)
        )

    def test_empty_repository(self) -> None:
        linked_res = LinkedSemanticResult(
            original_result=ProjectSemanticResult(files={}, cross_file_references=[], diagnostics=[]),
            symbol_index=ProjectSymbolIndex(files={}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )
        res = self.builder.build_context(linked_result=linked_res)
        
        self.assertEqual(res.symbols, [])
        self.assertEqual(res.sections, [])

    def test_single_symbol_mapping_and_serialization(self) -> None:
        sym = ProjectSymbol(
            id="sym-add",
            name="add",
            qualified_name="src.math.add",
            kind=SymbolKind.FUNCTION,
            location=self.dummy_loc,
            visibility=VisibilityKind.PUBLIC
        )
        file_obj = ProjectFile(path=Path("src/math.py"), symbols=[sym], imports=[], exports=[], references=[])
        semantic_result = ProjectSemanticResult(
            files={Path("src/math.py"): file_obj},
            cross_file_references=[],
            diagnostics=[]
        )
        linked_res = LinkedSemanticResult(
            original_result=semantic_result,
            symbol_index=ProjectSymbolIndex(files={Path("src/math.py"): file_obj}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )

        res = self.builder.build_context(target_symbol_id="sym-add", linked_result=linked_res)

        self.assertEqual(len(res.symbols), 1)
        sym_ctx = res.symbols[0]
        self.assertEqual(sym_ctx.symbol_id, "sym-add")
        self.assertEqual(sym_ctx.qualified_name, "src.math.add")
        self.assertEqual(sym_ctx.kind, "function")
        self.assertIn("L5:4-L8:0", sym_ctx.definition_summary)
        
        # Metadata checks
        self.assertEqual(sym_ctx.metadata["name"], "add")
        self.assertEqual(sym_ctx.metadata["exported_status"], "false")
        self.assertEqual(sym_ctx.metadata["source_file"], "src/math.py")

        # Check serialization
        dump = res.model_dump()
        self.assertEqual(dump["symbols"][0]["symbol_id"], "sym-add")

    def test_multiple_symbols_ordering(self) -> None:
        sym_z = ProjectSymbol(
            id="sym-z", name="z", qualified_name="src.math.z", kind=SymbolKind.VARIABLE, location=self.dummy_loc, visibility=VisibilityKind.PUBLIC
        )
        sym_a = ProjectSymbol(
            id="sym-a", name="a", qualified_name="src.math.a", kind=SymbolKind.VARIABLE, location=self.dummy_loc, visibility=VisibilityKind.PUBLIC
        )
        file_obj = ProjectFile(path=Path("src/math.py"), symbols=[sym_z, sym_a], imports=[], exports=[], references=[])
        semantic_result = ProjectSemanticResult(files={Path("src/math.py"): file_obj}, cross_file_references=[], diagnostics=[])
        linked_res = LinkedSemanticResult(
            original_result=semantic_result,
            symbol_index=ProjectSymbolIndex(files={Path("src/math.py"): file_obj}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )

        res = self.builder.build_context(linked_result=linked_res)

        # Expected sorted order: a, then z
        self.assertEqual(len(res.symbols), 2)
        self.assertEqual(res.symbols[0].symbol_id, "sym-a")
        self.assertEqual(res.symbols[1].symbol_id, "sym-z")

    def test_exported_and_imported_symbols(self) -> None:
        sym = ProjectSymbol(
            id="sym-add", name="add", qualified_name="src.math.add", kind=SymbolKind.FUNCTION, location=self.dummy_loc, visibility=VisibilityKind.PUBLIC
        )
        exp = ExportDeclaration(exported_name="add", local_symbol_id="sym-add", location=self.dummy_loc)
        file_math = ProjectFile(path=Path("src/math.py"), symbols=[sym], imports=[], exports=[exp], references=[])
        
        # User importing 'add' from main.py
        main_loc = SymbolLocation(
            file_path=Path("src/main.py"),
            location=Location(start_line=1, start_column=0, end_line=2, end_column=0)
        )
        imp = ImportDeclaration(imported_name="add", module_specifier="./math", location=main_loc)
        file_main = ProjectFile(path=Path("src/main.py"), symbols=[], imports=[imp], exports=[], references=[])

        semantic_result = ProjectSemanticResult(
            files={Path("src/math.py"): file_math, Path("src/main.py"): file_main},
            cross_file_references=[],
            diagnostics=[]
        )

        resolved_imp = ResolvedImport(
            import_declaration=imp,
            target_file=Path("src/math.py"),
            target_symbol=sym
        )

        linked_res = LinkedSemanticResult(
            original_result=semantic_result,
            symbol_index=ProjectSymbolIndex(files={Path("src/math.py"): file_math, Path("src/main.py"): file_main}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[resolved_imp], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )

        res = self.builder.build_context(target_symbol_id="sym-add", linked_result=linked_res)

        self.assertEqual(len(res.symbols), 1)
        sym_ctx = res.symbols[0]
        self.assertEqual(sym_ctx.metadata["exported_status"], "true")
        self.assertEqual(sym_ctx.metadata["imported_usages"], "src/main.py")

    def test_dependency_call_and_architecture_relationships(self) -> None:
        sym1 = ProjectSymbol(
            id="sym-1", name="sym1", qualified_name="src.sym1", kind=SymbolKind.FUNCTION, location=self.dummy_loc, visibility=VisibilityKind.PUBLIC
        )
        sym2 = ProjectSymbol(
            id="sym-2", name="sym2", qualified_name="src.sym2", kind=SymbolKind.FUNCTION, location=self.dummy_loc, visibility=VisibilityKind.PUBLIC
        )
        file_obj = ProjectFile(path=Path("src/sym.py"), symbols=[sym1, sym2], imports=[], exports=[], references=[])
        semantic_result = ProjectSemanticResult(files={Path("src/sym.py"): file_obj}, cross_file_references=[], diagnostics=[])
        linked_res = LinkedSemanticResult(
            original_result=semantic_result,
            symbol_index=ProjectSymbolIndex(files={Path("src/sym.py"): file_obj}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )

        # Graph containing:
        # sym-1 -> sym-2 (CALLS)
        # sym-2 -> sym-1 (USAGE)
        nodes = [
            GraphNode(id="sym-1", name="sym1", type=DependencyNodeType.FUNCTION),
            GraphNode(id="sym-2", name="sym2", type=DependencyNodeType.FUNCTION),
        ]
        edges = [
            GraphEdge(source_id="sym-1", target_id="sym-2", type=DependencyEdgeType.CALLS),
            GraphEdge(source_id="sym-2", target_id="sym-1", type=DependencyEdgeType.USAGE)
        ]
        graph = DependencyGraph(nodes=nodes, edges=edges)

        # Architecture layer
        layers = [
            ArchitectureLayer(id="logic", name="Logic", layer_type=LayerType.DOMAIN, node_ids=["sym-1", "sym-2"])
        ]
        issues = [
            ArchitectureIssue(
                id="iss-1", title="Warning", description="Issue on sym1", severity=SeverityLevel.ERROR, category=AnalysisCategory.SMELL, recommendation="Fix", location="sym-1"
            )
        ]
        arch_res = ArchitectureAnalysisResult(issues=issues, layers=layers, metrics=[], diagnostics=[])

        res = self.builder.build_context(linked_result=linked_res, graph=graph, arch_result=arch_res)

        # Retrieve sym-1 context
        ctx1 = next(c for c in res.symbols if c.symbol_id == "sym-1")
        self.assertEqual(ctx1.dependencies, ["sym-2"])
        self.assertEqual(ctx1.dependents, ["sym-2"])
        self.assertEqual(ctx1.metadata["calls_out"], "sym-2")
        self.assertEqual(ctx1.metadata["calls_in"], "")
        self.assertEqual(ctx1.metadata["architecture_layer"], "logic")
        self.assertIn("Issue on sym1", ctx1.metadata["diagnostics"])

        # Retrieve sym-2 context
        ctx2 = next(c for c in res.symbols if c.symbol_id == "sym-2")
        self.assertEqual(ctx2.dependencies, ["sym-1"])
        self.assertEqual(ctx2.dependents, ["sym-1"]) # sym-1 calls sym-2
        self.assertEqual(ctx2.metadata["calls_in"], "sym-1")
        self.assertEqual(ctx2.metadata["calls_out"], "")

    def test_deterministic_hashes_and_statelessness(self) -> None:
        sym = ProjectSymbol(
            id="sym-add", name="add", qualified_name="src.math.add", kind=SymbolKind.FUNCTION, location=self.dummy_loc, visibility=VisibilityKind.PUBLIC
        )
        file_obj = ProjectFile(path=Path("src/math.py"), symbols=[sym], imports=[], exports=[], references=[])
        semantic_result = ProjectSemanticResult(files={Path("src/math.py"): file_obj}, cross_file_references=[], diagnostics=[])
        linked_res = LinkedSemanticResult(
            original_result=semantic_result,
            symbol_index=ProjectSymbolIndex(files={Path("src/math.py"): file_obj}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )

        res1 = self.builder.build_context(target_symbol_id="sym-add", linked_result=linked_res)
        res2 = self.builder.build_context(target_symbol_id="sym-add", linked_result=linked_res)

        self.assertEqual(res1.id, res2.id)
        self.assertEqual(res1, res2)

    def test_thread_safety_and_concurrency(self) -> None:
        sym = ProjectSymbol(
            id="sym-add", name="add", qualified_name="src.math.add", kind=SymbolKind.FUNCTION, location=self.dummy_loc, visibility=VisibilityKind.PUBLIC
        )
        file_obj = ProjectFile(path=Path("src/math.py"), symbols=[sym], imports=[], exports=[], references=[])
        semantic_result = ProjectSemanticResult(files={Path("src/math.py"): file_obj}, cross_file_references=[], diagnostics=[])
        linked_res = LinkedSemanticResult(
            original_result=semantic_result,
            symbol_index=ProjectSymbolIndex(files={Path("src/math.py"): file_obj}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )

        def run_build():
            return self.builder.build_context(target_symbol_id="sym-add", linked_result=linked_res)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_build) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for r in results:
            self.assertEqual(r, first)


if __name__ == "__main__":
    unittest.main()
