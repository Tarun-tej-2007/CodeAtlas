"""AI Analysis Integration and Validation tests for the complete AI Analysis Subsystem."""

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
    FindingAnalyzer,
    RecommendationEngine,
    SummaryEngine,
    ReportBuilder,
    PromptContextBuilder,
)


class TestAIAnalysisValidation(unittest.TestCase):
    """Exercises the complete AI Analysis pipeline end-to-end under concurrent stress loads."""

    def setUp(self) -> None:
        self.finding_analyzer = FindingAnalyzer()
        self.rec_engine = RecommendationEngine()
        self.summary_engine = SummaryEngine()
        self.report_builder = ReportBuilder()
        self.prompt_context_builder = PromptContextBuilder()

        # Seed mock repository profile with a multi-language setup
        self.repo = RepositoryContext(
            repo_name="validation-app",
            file_paths=["src/main.py", "src/helper.js", "src/styles.css"],
            primary_languages=["python", "javascript", "css"]
        )

        # Core coupling symbol
        self.symbol = SymbolContext(
            symbol_id="sym-core",
            qualified_name="src.main.Core",
            kind="class",
            definition_summary="Core module entrypoint.",
            dependencies=[],
            dependents=[f"sym-client-{i}" for i in range(12)],
            metadata={"source_file": "src/main.py"}
        )

        self.context = AIContextResult(
            id="ctx-123",
            context_type=ContextType.FILE,
            granularity=SummaryGranularity.COMPACT,
            sections=[],
            symbols=[self.symbol],
            repository=self.repo
        )

        # Graph node hub
        nodes = [
            GraphNode(id="src/main.py", name="main", type=DependencyNodeType.MODULE),
        ]
        edges = []
        for i in range(21):
            tgt = f"src/dep_{i}.py"
            nodes.append(GraphNode(id=tgt, name=f"dep_{i}", type=DependencyNodeType.MODULE))
            edges.append(GraphEdge(source_id="src/main.py", target_id=tgt, type=DependencyEdgeType.USAGE))
        self.graph = DependencyGraph(nodes=nodes, edges=edges)

        # Layer violation architecture issue
        layers = [ArchitectureLayer(id="pres", name="Pres", layer_type=LayerType.PRESENTATION, node_ids=["src/main.py"])]
        issues = [
            ArchitectureIssue(
                id="iss-layer",
                title="Invalid Layer Call",
                description="Presentation depends on infrastructure directly.",
                severity=SeverityLevel.ERROR,
                category=AnalysisCategory.LAYERING,
                recommendation="Fix imports",
                location="src/main.py"
            )
        ]
        self.arch_result = ArchitectureAnalysisResult(issues=issues, layers=layers, metrics=[], diagnostics=[])

    def test_complete_end_to_end_analysis_pipeline(self) -> None:
        # 1. Run Finding Analyzer -> generates findings
        res_findings = self.finding_analyzer.analyze(
            context_result=self.context, graph=self.graph, arch_result=self.arch_result
        )
        self.assertEqual(len(res_findings.findings), 4)  # Multi-lang, high-coupling, graph hub, layer violation
        self.assertEqual(res_findings.recommendations, [])

        # 2. Run Recommendation Engine -> adds recommendations
        res_recs = self.rec_engine.generate_recommendations(res_findings)
        self.assertEqual(len(res_recs.findings), 4)
        self.assertEqual(len(res_recs.recommendations), 4)

        # 3. Run Summary Engine -> calculates summary tallies
        res_summary = self.summary_engine.summarize(res_recs)
        self.assertEqual(res_summary.summary.total_findings, 4)
        self.assertEqual(res_summary.summary.findings_by_severity, {"warning": 3, "error": 1})
        self.assertEqual(res_summary.summary.metadata["total_recommendations"], "4")

        # 4. Run Report Builder -> builds markdown report
        report = self.report_builder.build_report(res_summary)
        self.assertEqual(len(report.sections), 4)  # Summary, findings, recs, logs
        self.assertIn("Total Findings**: 4", report.sections[0].content)

        # 5. Run Prompt Context Builder -> builds LLM prompt context
        prompt_ctx = self.prompt_context_builder.build_prompt_context(report=report, result=res_summary)
        # summary-context (priority 1), findings-context (priority 2), recs-context (priority 2), 4 report sections (priority 3)
        self.assertEqual(len(prompt_ctx.sections), 7)
        self.assertEqual(prompt_ctx.sections[0].id, "summary-context")

        # Assert serialization compatibility
        json_str = prompt_ctx.model_dump_json()
        self.assertIn("Core", json_str)

    def test_empty_repository_handling(self) -> None:
        empty_repo = RepositoryContext(repo_name="empty-app", file_paths=[], primary_languages=[])
        empty_ctx = AIContextResult(
            id="ctx-empty", context_type=ContextType.FILE, granularity=SummaryGranularity.COMPACT, sections=[], symbols=[], repository=empty_repo
        )
        empty_graph = DependencyGraph(nodes=[], edges=[])
        empty_arch = ArchitectureAnalysisResult(issues=[], layers=[], metrics=[], diagnostics=[])

        # Execute complete pipeline
        res_findings = self.finding_analyzer.analyze(
            context_result=empty_ctx, graph=empty_graph, arch_result=empty_arch
        )
        res_recs = self.rec_engine.generate_recommendations(res_findings)
        res_summary = self.summary_engine.summarize(res_recs)
        report = self.report_builder.build_report(res_summary)
        prompt_ctx = self.prompt_context_builder.build_prompt_context(report=report, result=res_summary)

        # Assert output
        self.assertEqual(res_summary.summary.total_findings, 1)  # Repo Empty finding
        self.assertEqual(res_summary.summary.findings_by_severity, {"info": 1})
        self.assertEqual(len(report.sections), 4)  # Summary + Findings + Recs + Logs
        self.assertEqual(len(prompt_ctx.sections), 7)  # summary-context, findings-context, recs-context, 4 report sections

    def test_pipeline_thread_safety_and_determinism(self) -> None:
        def execute_pipeline():
            res_findings = self.finding_analyzer.analyze(
                context_result=self.context, graph=self.graph, arch_result=self.arch_result
            )
            res_recs = self.rec_engine.generate_recommendations(res_findings)
            res_summary = self.summary_engine.summarize(res_recs)
            report = self.report_builder.build_report(res_summary)
            return self.prompt_context_builder.build_prompt_context(report=report, result=res_summary)

        # Determinism check
        pc1 = execute_pipeline()
        pc2 = execute_pipeline()
        self.assertEqual(pc1.id, pc2.id)
        self.assertEqual(pc1.sections, pc2.sections)

        # Concurrency stress test
        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(execute_pipeline) for _ in range(20)]
            results = [f.result() for f in futures]

        for p in results:
            self.assertEqual(p, pc1)


if __name__ == "__main__":
    unittest.main()
