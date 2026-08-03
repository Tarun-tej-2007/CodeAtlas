"""Unit tests for the Finding Analyzer."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.graph.enums import DependencyEdgeType, DependencyNodeType
from app.graph.dependency_models import GraphNode, GraphEdge
from app.graph.dependency_graph import DependencyGraph

from app.ai.enums import ContextType, SummaryGranularity
from app.ai.models import AIContextResult, RepositoryContext, SymbolContext

from app.architecture.enums import LayerType, SeverityLevel, AnalysisCategory
from app.architecture.models import ArchitectureLayer, ArchitectureIssue, ArchitectureAnalysisResult

from app.analysis import (
    AnalysisSeverity,
    AnalysisType,
    AnalysisFinding,
    FindingAnalyzer,
)


class TestFindingAnalyzer(unittest.TestCase):
    """Verifies finding compilation rules, graph hub warnings, architecture mappings, and concurrency safety."""

    def setUp(self) -> None:
        self.analyzer = FindingAnalyzer()

    def test_empty_inputs(self) -> None:
        res = self.analyzer.analyze(context_result=None, graph=None, arch_result=None)
        
        self.assertEqual(res.findings, [])
        self.assertEqual(res.summary.total_findings, 0)
        self.assertEqual(res.summary.findings_by_severity, {})

    def test_repository_findings(self) -> None:
        # 1. Test empty repository finding
        repo_empty = RepositoryContext(repo_name="empty-app", file_paths=[], primary_languages=[])
        ctx_empty = AIContextResult(
            id="run-1", context_type=ContextType.FILE, granularity=SummaryGranularity.COMPACT, sections=[], symbols=[], repository=repo_empty
        )
        res_empty = self.analyzer.analyze(context_result=ctx_empty)
        
        self.assertEqual(len(res_empty.findings), 1)
        self.assertEqual(res_empty.findings[0].title, "Empty Repository Structure")
        self.assertEqual(res_empty.findings[0].severity, AnalysisSeverity.INFO)

        # 2. Test multi-language repository finding
        repo_multi = RepositoryContext(repo_name="multi-app", file_paths=["a.py", "b.js", "c.ts"], primary_languages=["python", "javascript", "typescript"])
        ctx_multi = AIContextResult(
            id="run-2", context_type=ContextType.FILE, granularity=SummaryGranularity.COMPACT, sections=[], symbols=[], repository=repo_multi
        )
        res_multi = self.analyzer.analyze(context_result=ctx_multi)
        
        self.assertEqual(len(res_multi.findings), 1)
        self.assertEqual(res_multi.findings[0].title, "Multi-Language System Complexity")
        self.assertEqual(res_multi.findings[0].severity, AnalysisSeverity.WARNING)

    def test_symbol_findings(self) -> None:
        # High dependents (coupling afferent > 10)
        sym = SymbolContext(
            symbol_id="sym-core",
            qualified_name="src.core.Core",
            kind="class",
            definition_summary="...",
            dependencies=[],
            dependents=[f"sym-client-{i}" for i in range(12)],
            metadata={"source_file": "src/core.py"}
        )
        ctx = AIContextResult(
            id="run-1", context_type=ContextType.SYMBOL, granularity=SummaryGranularity.DETAILED, sections=[], symbols=[sym], repository=None
        )
        res = self.analyzer.analyze(context_result=ctx)

        self.assertEqual(len(res.findings), 1)
        self.assertEqual(res.findings[0].title, "Highly Coupled Core Symbol")
        self.assertEqual(res.findings[0].severity, AnalysisSeverity.WARNING)
        self.assertEqual(res.findings[0].file_path, "src/core.py")

    def test_dependency_findings(self) -> None:
        # Construct a node with high connection degree (> 20)
        nodes = [
            GraphNode(id="src/hub.py", name="hub", type=DependencyNodeType.MODULE),
        ]
        # 22 outgoing edges
        edges = []
        for i in range(22):
            tgt_id = f"src/dep_{i}.py"
            nodes.append(GraphNode(id=tgt_id, name=f"dep_{i}", type=DependencyNodeType.MODULE))
            edges.append(GraphEdge(source_id="src/hub.py", target_id=tgt_id, type=DependencyEdgeType.USAGE))
        graph = DependencyGraph(nodes=nodes, edges=edges)

        res = self.analyzer.analyze(graph=graph)

        self.assertEqual(len(res.findings), 1)
        self.assertEqual(res.findings[0].title, "High Connection Graph Hub")
        self.assertEqual(res.findings[0].severity, AnalysisSeverity.WARNING)
        self.assertEqual(res.findings[0].file_path, "src/hub.py")

    def test_architecture_findings(self) -> None:
        layers = [ArchitectureLayer(id="pres", name="Pres", layer_type=LayerType.PRESENTATION, node_ids=["n1"])]
        issues = [
            ArchitectureIssue(
                id="iss-layer",
                title="Invalid Layer Call",
                description="Presentation depends on infrastructure directly.",
                severity=SeverityLevel.ERROR,
                category=AnalysisCategory.LAYERING,
                recommendation="Fix it",
                location="pres"
            )
        ]
        arch_res = ArchitectureAnalysisResult(issues=issues, layers=layers, metrics=[], diagnostics=[])

        res = self.analyzer.analyze(arch_result=arch_res)

        self.assertEqual(len(res.findings), 1)
        finding = res.findings[0]
        self.assertEqual(finding.title, "Invalid Layer Call")
        self.assertEqual(finding.severity, AnalysisSeverity.ERROR)
        self.assertEqual(finding.file_path, "pres")

    def test_deterministic_ordering_and_serialization(self) -> None:
        repo = RepositoryContext(repo_name="multi-app", file_paths=["a.py", "b.js", "c.ts"], primary_languages=["python", "javascript", "typescript"])
        ctx = AIContextResult(
            id="run-1", context_type=ContextType.FILE, granularity=SummaryGranularity.COMPACT, sections=[], symbols=[], repository=repo
        )
        
        res1 = self.analyzer.analyze(context_result=ctx)
        res2 = self.analyzer.analyze(context_result=ctx)

        # Check determinism
        self.assertEqual(res1.id, res2.id)
        self.assertEqual(res1.findings, res2.findings)

        # Check serialization compatibility
        dump = res1.model_dump()
        self.assertIn("analysis-run", dump["id"])
        
        json_str = res1.model_dump_json()
        self.assertIn("Multi-Language System Complexity", json_str)

    def test_immutability(self) -> None:
        finding = AnalysisFinding(
            id="f-1",
            title="Smell",
            description="Bad class",
            severity=AnalysisSeverity.WARNING,
            file_path="src/main.py",
            start_line=10,
            end_line=12
        )
        with self.assertRaises((ValidationError, TypeError)):
            finding.start_line = 5  # type: ignore

    def test_thread_safety_and_concurrency(self) -> None:
        repo = RepositoryContext(repo_name="multi-app", file_paths=["a.py", "b.js", "c.ts"], primary_languages=["python", "javascript", "typescript"])
        ctx = AIContextResult(
            id="run-1", context_type=ContextType.FILE, granularity=SummaryGranularity.COMPACT, sections=[], symbols=[], repository=repo
        )

        def run_analyze():
            return self.analyzer.analyze(context_result=ctx)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_analyze) for _ in range(20)]
            results = [f.result() for f in futures]

        first = results[0]
        for r in results:
            self.assertEqual(r.id, first.id)
            self.assertEqual(r.findings, first.findings)


if __name__ == "__main__":
    unittest.main()
