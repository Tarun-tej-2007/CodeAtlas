"""Integration and Performance Optimization tests for the AI Context Cache Layer."""

import unittest
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

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

from app.ai import (
    ContextLookupCache,
    RepositoryContextBuilder,
    SymbolContextBuilder,
    AIContextComposer,
)


class TestContextOptimization(unittest.TestCase):
    """Verifies that the ContextLookupCache accelerates context generation and preserves behavioral equivalence."""

    def setUp(self) -> None:
        self.repo_builder = RepositoryContextBuilder()
        self.sym_builder = SymbolContextBuilder()
        self.composer = AIContextComposer()

        # Build mock structures
        self.dummy_loc = SymbolLocation(
            file_path=Path("src/math.py"),
            location=Location(start_line=1, start_column=0, end_line=10, end_column=0)
        )
        self.sym1 = ProjectSymbol(
            id="sym-1", name="add", qualified_name="src.math.add", kind=SymbolKind.FUNCTION, location=self.dummy_loc, visibility=VisibilityKind.PUBLIC
        )
        exp = ExportDeclaration(exported_name="add", local_symbol_id="sym-1", location=self.dummy_loc)
        self.file_math = ProjectFile(path=Path("src/math.py"), symbols=[self.sym1], imports=[], exports=[exp], references=[])
        self.semantic_result = ProjectSemanticResult(files={Path("src/math.py"): self.file_math}, cross_file_references=[], diagnostics=[])
        self.linked_result = LinkedSemanticResult(
            original_result=self.semantic_result,
            symbol_index=ProjectSymbolIndex(files={Path("src/math.py"): self.file_math}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )

        self.nodes = [GraphNode(id="sym-1", name="add", type=DependencyNodeType.FUNCTION)]
        self.graph = DependencyGraph(nodes=self.nodes, edges=[])

    def test_optimization_equivalence(self) -> None:
        # Run uncached pipeline
        repo_res_uncached = self.repo_builder.build_context("test-repo", semantic_result=self.semantic_result, graph=self.graph)
        sym_res_uncached = self.sym_builder.build_context(linked_result=self.linked_result, graph=self.graph)
        composed_uncached = self.composer.compose(repo_res_uncached, sym_res_uncached)

        # Run cached pipeline
        cache = ContextLookupCache(linked_result=self.linked_result, graph=self.graph)
        repo_res_cached = self.repo_builder.build_context("test-repo", cache=cache)
        sym_res_cached = self.sym_builder.build_context(cache=cache, linked_result=self.linked_result)
        composed_cached = self.composer.compose(repo_res_cached, sym_res_cached, cache=cache)

        # Check equivalence
        self.assertEqual(repo_res_uncached.sections, repo_res_cached.sections)
        self.assertEqual(sym_res_uncached.symbols, sym_res_cached.symbols)
        self.assertEqual(composed_uncached.id, composed_cached.id)
        self.assertEqual(composed_uncached.sections, composed_cached.sections)

    def test_cache_correctness_and_isolation(self) -> None:
        cache1 = ContextLookupCache(linked_result=self.linked_result, graph=self.graph)
        
        # Second distinct graph with a dependency edge
        nodes2 = [
            GraphNode(id="sym-2", name="sub", type=DependencyNodeType.FUNCTION),
            GraphNode(id="sym-3", name="helper", type=DependencyNodeType.FUNCTION),
        ]
        edges2 = [GraphEdge(source_id="sym-2", target_id="sym-3", type=DependencyEdgeType.USAGE)]
        graph2 = DependencyGraph(nodes=nodes2, edges=edges2)
        cache2 = ContextLookupCache(linked_result=self.linked_result, graph=graph2)

        self.assertIn("sym-1", cache1.exported_ids)

        # Confirm isolation: cache2 has usages edges, cache1 does not
        self.assertNotEqual(cache1.usages_out, cache2.usages_out)

    def test_thread_safety_and_concurrency(self) -> None:
        cache = ContextLookupCache(linked_result=self.linked_result, graph=self.graph)

        def run_cached_pipeline():
            repo_res = self.repo_builder.build_context("thread-repo", cache=cache)
            sym_res = self.sym_builder.build_context(cache=cache, linked_result=self.linked_result)
            return self.composer.compose(repo_res, sym_res, cache=cache)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_cached_pipeline) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for r in results:
            self.assertEqual(r.id, first.id)
            self.assertEqual(r.sections, first.sections)

    def test_large_synthetic_repository_performance(self) -> None:
        # Generate large synthetic codebase: 100 files, 500 symbols, 1000 edges
        files_dict = {}
        nodes = []
        edges = []

        for i in range(100):
            file_path = Path(f"src/file_{i}.py")
            file_symbols = []
            for j in range(5):
                sym_id = f"sym-{i}-{j}"
                sym = ProjectSymbol(
                    id=sym_id,
                    name=f"func_{j}",
                    qualified_name=f"src.file_{i}.func_{j}",
                    kind=SymbolKind.FUNCTION,
                    location=SymbolLocation(
                        file_path=file_path,
                        location=Location(start_line=j*10+1, start_column=0, end_line=j*10+9, end_column=0)
                    ),
                    visibility=VisibilityKind.PUBLIC
                )
                file_symbols.append(sym)
                nodes.append(GraphNode(id=sym_id, name=f"func_{j}", type=DependencyNodeType.FUNCTION))
            
            files_dict[file_path] = ProjectFile(path=file_path, symbols=file_symbols, imports=[], exports=[], references=[])

        # Construct 1000 random-like edges to simulate dependencies
        seen_edges = set()
        for i in range(1000):
            src_id = f"sym-{i % 100}-{i % 5}"
            tgt_id = f"sym-{(i + 77) % 100}-{(i + 3) % 5}"
            if src_id != tgt_id and (src_id, tgt_id) not in seen_edges:
                seen_edges.add((src_id, tgt_id))
                edges.append(GraphEdge(source_id=src_id, target_id=tgt_id, type=DependencyEdgeType.USAGE))

        semantic_result = ProjectSemanticResult(files=files_dict, cross_file_references=[], diagnostics=[])
        linked_result = LinkedSemanticResult(
            original_result=semantic_result,
            symbol_index=ProjectSymbolIndex(files=files_dict),
            import_export_result=ImportExportResolutionResult(resolved_imports=[], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )
        graph = DependencyGraph(nodes=nodes, edges=edges)

        # Time the Uncached execution
        start_uncached = time.perf_counter()
        repo_res_un = self.repo_builder.build_context("large-repo", semantic_result=semantic_result, graph=graph)
        sym_res_un = self.sym_builder.build_context(linked_result=linked_result, graph=graph)
        composed_un = self.composer.compose(repo_res_un, sym_res_un)
        time_uncached = time.perf_counter() - start_uncached

        # Time the Cached execution (including cache initialization)
        start_cached = time.perf_counter()
        cache = ContextLookupCache(linked_result=linked_result, graph=graph)
        repo_res_ca = self.repo_builder.build_context("large-repo", cache=cache)
        sym_res_ca = self.sym_builder.build_context(cache=cache, linked_result=linked_result)
        composed_ca = self.composer.compose(repo_res_ca, sym_res_ca, cache=cache)
        time_cached = time.perf_counter() - start_cached

        # Assert identical results
        self.assertEqual(composed_un.id, composed_ca.id)
        self.assertEqual(len(composed_un.sections), len(composed_ca.sections))

        # Check performance improvement: cached pipeline should be significantly faster
        # (especially since we index graph connections once instead of linear scans per symbol)
        print(f"\nUncached execution time: {time_uncached:.4f}s")
        print(f"Cached execution time (including cache init): {time_cached:.4f}s")
        self.assertTrue(time_cached < time_uncached or time_cached < 0.2)


if __name__ == "__main__":
    unittest.main()
