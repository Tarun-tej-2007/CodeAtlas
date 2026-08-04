"""Comprehensive Integration and Validation tests for the complete AI Context Subsystem."""

import unittest
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
    ContextPriority,
    ContextType,
    SummaryGranularity,
    ContextSection,
    SymbolContext,
    RepositoryContext,
    AIContextResult,
    RepositoryContextBuilder,
    SymbolContextBuilder,
    AIContextComposer,
    ContextLookupCache,
)


class TestAIContextValidation(unittest.TestCase):
    """Exercises the complete AI Context generation pipeline end-to-end under concurrent stress loads."""

    def setUp(self) -> None:
        self.repo_builder = RepositoryContextBuilder()
        self.sym_builder = SymbolContextBuilder()
        self.composer = AIContextComposer()

        # Construct standard mock metadata
        self.dummy_loc = SymbolLocation(
            file_path=Path("src/views.py"),
            location=Location(start_line=1, start_column=0, end_line=10, end_column=0)
        )
        self.sym_view = ProjectSymbol(
            id="sym-view", name="View", qualified_name="src.views.View", kind=SymbolKind.CLASS, location=self.dummy_loc, visibility=VisibilityKind.PUBLIC
        )
        self.file_views = ProjectFile(path=Path("src/views.py"), symbols=[self.sym_view], imports=[], exports=[], references=[])

        self.semantic_result = ProjectSemanticResult(files={Path("src/views.py"): self.file_views}, cross_file_references=[], diagnostics=[])
        self.linked_result = LinkedSemanticResult(
            original_result=self.semantic_result,
            symbol_index=ProjectSymbolIndex(files={Path("src/views.py"): self.file_views}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )

        self.nodes = [GraphNode(id="sym-view", name="View", type=DependencyNodeType.CLASS)]
        self.graph = DependencyGraph(nodes=self.nodes, edges=[])

    def test_complete_context_generation_pipeline(self) -> None:
        # 1. Initialize execution-scoped cache
        cache = ContextLookupCache(linked_result=self.linked_result, graph=self.graph)

        # 2. Build repository context
        repo_res = self.repo_builder.build_context("validation-app", cache=cache)
        self.assertEqual(repo_res.repository.repo_name, "validation-app")
        self.assertEqual(len(repo_res.sections), 2)  # Overview + dependencies

        # 3. Build symbol context
        sym_res = self.sym_builder.build_context(cache=cache, linked_result=self.linked_result)
        self.assertEqual(len(sym_res.symbols), 1)

        # 4. Compose unified context Result
        composed_res = self.composer.compose(repo_res, sym_res, cache=cache)

        # 5. Assertions on merged payload
        self.assertEqual(composed_res.repository.repo_name, "validation-app")
        self.assertEqual(len(composed_res.symbols), 1)
        self.assertEqual(composed_res.symbols[0].symbol_id, "sym-view")
        
        # Combined sections (Overview + dependencies + symbol-context-sym-view = 3)
        self.assertEqual(len(composed_res.sections), 3)

        # Check sorting order: HIGH priority overview, then MEDIUM dependencies & symbol sections
        self.assertEqual(composed_res.sections[0].id, "repo-overview")
        self.assertEqual(composed_res.sections[0].priority, ContextPriority.HIGH)

        # Assert serialization compatibility
        json_str = composed_res.model_dump_json()
        self.assertIn("validation-app", json_str)
        self.assertIn("sym-view", json_str)

    def test_empty_repository_edge_case(self) -> None:
        semantic_empty = ProjectSemanticResult(files={}, cross_file_references=[], diagnostics=[])
        linked_empty = LinkedSemanticResult(
            original_result=semantic_empty,
            symbol_index=ProjectSymbolIndex(files={}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )
        graph_empty = DependencyGraph(nodes=[], edges=[])

        cache = ContextLookupCache(linked_result=linked_empty, graph=graph_empty)

        repo_res = self.repo_builder.build_context("empty-app", cache=cache)
        sym_res = self.sym_builder.build_context(cache=cache, linked_result=linked_empty)
        composed_res = self.composer.compose(repo_res, sym_res, cache=cache)

        self.assertEqual(composed_res.repository.repo_name, "empty-app")
        self.assertEqual(composed_res.symbols, [])
        self.assertEqual(len(composed_res.sections), 1)  # Only Overview section
        self.assertIn("Total Analyzed Files: 0", composed_res.sections[0].content)

    def test_pipeline_thread_safety(self) -> None:
        cache = ContextLookupCache(linked_result=self.linked_result, graph=self.graph)

        def run_pipeline():
            repo_res = self.repo_builder.build_context("concurrency-app", cache=cache)
            sym_res = self.sym_builder.build_context(cache=cache, linked_result=self.linked_result)
            return self.composer.compose(repo_res, sym_res, cache=cache)

        # Stress test pipeline concurrency
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_pipeline) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for res in results:
            self.assertEqual(res.id, first.id)
            self.assertEqual(res.sections, first.sections)


if __name__ == "__main__":
    unittest.main()
