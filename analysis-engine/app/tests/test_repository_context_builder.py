"""Unit tests for the Repository Context Builder."""

import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import GraphNode, GraphEdge
from app.graph.dependency_graph import DependencyGraph

from app.semantic.enums import SymbolKind, VisibilityKind
from app.semantic.models import Location
from app.semantic.project_models import ProjectSemanticResult, ProjectFile, ProjectSymbol, SymbolLocation
from app.semantic.linking_pipeline import LinkedSemanticResult
from app.semantic.project_symbol_index import ProjectSymbolIndex
from app.semantic.import_export_resolver import ImportExportResolutionResult
from app.semantic.reference_resolver import ReferenceResolutionResult

from app.architecture.enums import LayerType, SeverityLevel, AnalysisCategory
from app.architecture.models import ArchitectureLayer, ArchitectureIssue, ArchitectureAnalysisResult

from app.ai import RepositoryContextBuilder, ContextPriority, ContextType


class TestRepositoryContextBuilder(unittest.TestCase):
    """Verifies repository-level overview summarization, thread safety, and deterministic run hashes."""

    def setUp(self) -> None:
        self.builder = RepositoryContextBuilder()
        self.dummy_loc = SymbolLocation(
            file_path=Path("src/foo.py"),
            location=Location(start_line=1, start_column=0, end_line=2, end_column=0)
        )

    def test_empty_repository(self) -> None:
        semantic_result = ProjectSemanticResult(files={}, cross_file_references=[], diagnostics=[])
        res = self.builder.build_context(
            repo_name="empty-repo",
            semantic_result=semantic_result,
            graph=None,
            arch_result=None
        )

        self.assertEqual(res.repository.repo_name, "empty-repo")
        self.assertEqual(res.repository.file_paths, [])
        self.assertEqual(res.repository.primary_languages, [])
        
        # Check that overview section exists
        overview_sec = next(s for s in res.sections if s.id == "repo-overview")
        self.assertIn("Total Analyzed Files: 0", overview_sec.content)
        self.assertIn("Languages Discovered: None", overview_sec.content)

    def test_single_file_and_symbols(self) -> None:
        # File 1: Python file with symbols
        sym1 = ProjectSymbol(
            id="sym-foo",
            name="Foo",
            qualified_name="src.foo.Foo",
            kind=SymbolKind.CLASS,
            location=self.dummy_loc,
            visibility=VisibilityKind.PUBLIC
        )
        sym2 = ProjectSymbol(
            id="sym-bar",
            name="bar",
            qualified_name="src.foo.bar",
            kind=SymbolKind.FUNCTION,
            location=self.dummy_loc,
            visibility=VisibilityKind.PUBLIC
        )
        file_obj = ProjectFile(path=Path("src/foo.py"), symbols=[sym1, sym2], imports=[], exports=[], references=[])
        
        semantic_result = ProjectSemanticResult(
            files={Path("src/foo.py"): file_obj},
            cross_file_references=[],
            diagnostics=[]
        )

        res = self.builder.build_context(
            repo_name="single-file-repo",
            semantic_result=semantic_result
        )

        self.assertEqual(res.repository.file_paths, ["src/foo.py"])
        self.assertEqual(res.repository.primary_languages, ["python"])
        
        overview_sec = next(s for s in res.sections if s.id == "repo-overview")
        self.assertIn("- class: 1", overview_sec.content)
        self.assertIn("- function: 1", overview_sec.content)

    def test_multi_language_and_linked_result(self) -> None:
        file_py = ProjectFile(path=Path("src/foo.py"), symbols=[], imports=[], exports=[], references=[])
        file_js = ProjectFile(path=Path("src/bar.js"), symbols=[], imports=[], exports=[], references=[])
        
        semantic_result = ProjectSemanticResult(
            files={Path("src/foo.py"): file_py, Path("src/bar.js"): file_js},
            cross_file_references=[],
            diagnostics=[]
        )

        # Mock LinkedSemanticResult
        linked_res = LinkedSemanticResult(
            original_result=semantic_result,
            symbol_index=ProjectSymbolIndex(files={}),
            import_export_result=ImportExportResolutionResult(resolved_imports=[], diagnostics=[]),
            reference_resolution_result=ReferenceResolutionResult(resolved_references=[], diagnostics=[])
        )

        res = self.builder.build_context(
            repo_name="multi-lang-repo",
            linked_result=linked_res
        )

        self.assertEqual(res.repository.file_paths, ["src/bar.js", "src/foo.py"])
        self.assertEqual(res.repository.primary_languages, ["javascript", "python"])

    def test_dependency_graph_and_architecture_integration(self) -> None:
        # Construct graph
        nodes = [
            GraphNode(id="n1", name="n1", type=DependencyNodeType.MODULE),
            GraphNode(id="n2", name="n2", type=DependencyNodeType.MODULE),
        ]
        edges = [
            GraphEdge(source_id="n1", target_id="n2", type=DependencyEdgeType.USAGE)
        ]
        graph = DependencyGraph(nodes=nodes, edges=edges)

        # Construct architecture
        layers = [
            ArchitectureLayer(id="pres", name="Pres", layer_type=LayerType.PRESENTATION, node_ids=["n1"]),
            ArchitectureLayer(id="dom", name="Dom", layer_type=LayerType.DOMAIN, node_ids=["n2"]),
        ]
        issues = [
            ArchitectureIssue(
                id="iss-1",
                title="Smell",
                description="Violated",
                severity=SeverityLevel.ERROR,
                category=AnalysisCategory.SMELL,
                recommendation="Fix it",
                location="pres"
            )
        ]
        arch_res = ArchitectureAnalysisResult(
            issues=issues,
            layers=layers,
            metrics=[],
            diagnostics=["Arch diagnostics complete"]
        )

        res = self.builder.build_context(
            repo_name="complex-repo",
            graph=graph,
            arch_result=arch_res
        )

        # Graph section should be present
        graph_sec = next(s for s in res.sections if s.id == "repo-dependencies")
        self.assertIn("Total Structural Nodes: 2", graph_sec.content)
        self.assertIn("Total Dependency Connections: 1", graph_sec.content)

        # Arch section should be present
        arch_sec = next(s for s in res.sections if s.id == "repo-architecture")
        self.assertIn("Detected Architectural Layers: 2", arch_sec.content)
        self.assertIn("Flagged Design Violations/Issues: 1", arch_sec.content)

    def test_serialization(self) -> None:
        semantic_result = ProjectSemanticResult(files={}, cross_file_references=[], diagnostics=[])
        res = self.builder.build_context("serialization-repo", semantic_result=semantic_result)
        
        dump = res.model_dump()
        self.assertIn("repo-context-run", dump["id"])
        self.assertEqual(dump["context_type"], ContextType.FILE)

        json_str = res.model_dump_json()
        self.assertIn("repo-overview", json_str)

    def test_deterministic_hashes(self) -> None:
        semantic_result = ProjectSemanticResult(files={}, cross_file_references=[], diagnostics=[])
        res1 = self.builder.build_context("determinism-repo", semantic_result=semantic_result)
        res2 = self.builder.build_context("determinism-repo", semantic_result=semantic_result)
        
        self.assertEqual(res1.id, res2.id)
        self.assertEqual(res1, res2)

    def test_thread_safety_and_concurrency(self) -> None:
        nodes = [GraphNode(id="n", name="n", type=DependencyNodeType.MODULE)]
        graph = DependencyGraph(nodes=nodes, edges=[])
        
        def run_build():
            return self.builder.build_context(
                repo_name="thread-repo",
                graph=graph
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_build) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for r in results:
            self.assertEqual(r, first)


if __name__ == "__main__":
    unittest.main()
