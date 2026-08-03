"""Unit tests for the AI Recommendation Engine."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from pydantic import ValidationError

from app.analysis import (
    AnalysisSeverity,
    AnalysisType,
    RecommendationStatus,
    AnalysisFinding,
    AnalysisRecommendation,
    AnalysisSummary,
    AnalysisResult,
    RecommendationEngine,
    RecommendationStrategy,
)


class CustomTestStrategy(RecommendationStrategy):
    """Custom strategy to verify extensibility."""

    def can_handle(self, finding: AnalysisFinding) -> bool:
        return finding.rule_id == "custom-rule"

    def generate(self, finding: AnalysisFinding) -> AnalysisRecommendation:
        return AnalysisRecommendation(
            id=f"rec-custom-{finding.id}",
            finding_id=finding.id,
            remediation="Apply custom patch",
            status=RecommendationStatus.OPEN,
            metadata={"priority": "high"}
        )


class TestRecommendationEngine(unittest.TestCase):
    """Verifies strategy mapping, duplicate deduplication, determinism, and extensibility."""

    def setUp(self) -> None:
        self.engine = RecommendationEngine()
        self.summary = AnalysisSummary(total_findings=0, findings_by_severity={}, duration_ms=10)

    def test_empty_analysis_results(self) -> None:
        empty_res = AnalysisResult(
            id="run-1", analysis_type=AnalysisType.DESIGN, summary=self.summary, findings=[]
        )
        res = self.engine.generate_recommendations(empty_res)
        self.assertEqual(res.recommendations, [])
        self.assertEqual(res.findings, [])

    def test_single_finding(self) -> None:
        finding = AnalysisFinding(
            id="f-1",
            title="Empty",
            description="Empty repository",
            severity=AnalysisSeverity.INFO,
            file_path="root",
            start_line=1,
            end_line=1,
            rule_id="repo-empty"
        )
        res = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=AnalysisSummary(total_findings=1, findings_by_severity={"info": 1}),
            findings=[finding]
        )

        res_opt = self.engine.generate_recommendations(res)
        self.assertEqual(len(res_opt.recommendations), 1)
        self.assertEqual(res_opt.recommendations[0].finding_id, "f-1")
        self.assertEqual(
            res_opt.recommendations[0].remediation,
            "Populate the repository with source files to begin code quality analysis."
        )
        self.assertEqual(res_opt.recommendations[0].status, RecommendationStatus.OPEN)

    def test_multiple_findings_and_priorities(self) -> None:
        # Construct multi-language and afferent coupling findings
        f1 = AnalysisFinding(
            id="f-1", title="Multi", description="...", severity=AnalysisSeverity.WARNING,
            file_path="root", start_line=1, end_line=1, rule_id="repo-multi-language"
        )
        f2 = AnalysisFinding(
            id="f-2", title="Afferent", description="...", severity=AnalysisSeverity.WARNING,
            file_path="src/core.py", start_line=10, end_line=10, rule_id="symbol-coupling-afferent"
        )
        res = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=AnalysisSummary(total_findings=2, findings_by_severity={"warning": 2}),
            findings=[f1, f2]
        )

        res_opt = self.engine.generate_recommendations(res)
        self.assertEqual(len(res_opt.recommendations), 2)
        # Recommendation IDs must be sorted alphabetically
        rec_ids = [r.id for r in res_opt.recommendations]
        self.assertEqual(rec_ids, sorted(rec_ids))

        # Check strategy assignments
        self.assertTrue(any("rec-multi" in r.id for r in res_opt.recommendations))
        self.assertTrue(any("rec-afferent" in r.id for r in res_opt.recommendations))

    def test_duplicate_recommendation_deduplication(self) -> None:
        # Two identical findings producing the same recommendation
        f1 = AnalysisFinding(
            id="f-1", title="Empty", description="Empty repository", severity=AnalysisSeverity.INFO,
            file_path="root", start_line=1, end_line=1, rule_id="repo-empty"
        )
        f2 = AnalysisFinding(
            id="f-1", title="Empty", description="Empty repository", severity=AnalysisSeverity.INFO,
            file_path="root", start_line=1, end_line=1, rule_id="repo-empty"
        )
        res = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=AnalysisSummary(total_findings=2, findings_by_severity={"info": 2}),
            findings=[f1, f2]
        )

        res_opt = self.engine.generate_recommendations(res)
        # Deduplication should yield exactly 1 recommendation DTO
        self.assertEqual(len(res_opt.recommendations), 1)

    def test_extensibility_with_custom_strategies(self) -> None:
        custom_engine = RecommendationEngine(strategies=[CustomTestStrategy()])
        finding = AnalysisFinding(
            id="f-custom", title="Custom", description="...", severity=AnalysisSeverity.WARNING,
            file_path="src/main.py", start_line=1, end_line=1, rule_id="custom-rule"
        )
        res = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=AnalysisSummary(total_findings=1, findings_by_severity={"warning": 1}),
            findings=[finding]
        )

        res_opt = custom_engine.generate_recommendations(res)
        self.assertEqual(len(res_opt.recommendations), 1)
        self.assertEqual(res_opt.recommendations[0].id, "rec-custom-f-custom")
        self.assertEqual(res_opt.recommendations[0].remediation, "Apply custom patch")

    def test_serialization_and_immutability(self) -> None:
        finding = AnalysisFinding(
            id="f-1", title="Empty", description="Empty repository", severity=AnalysisSeverity.INFO,
            file_path="root", start_line=1, end_line=1, rule_id="repo-empty"
        )
        res = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=AnalysisSummary(total_findings=1, findings_by_severity={"info": 1}),
            findings=[finding]
        )
        res_opt = self.engine.generate_recommendations(res)

        # Immutability: assert we cannot modify recommendations list directly
        with self.assertRaises((ValidationError, TypeError)):
            res_opt.recommendations = []  # type: ignore

        # Serialization
        dump = res_opt.model_dump()
        self.assertEqual(len(dump["recommendations"]), 1)
        self.assertEqual(dump["recommendations"][0]["finding_id"], "f-1")

    def test_repeated_execution_and_concurrency(self) -> None:
        finding = AnalysisFinding(
            id="f-1", title="Empty", description="Empty repository", severity=AnalysisSeverity.INFO,
            file_path="root", start_line=1, end_line=1, rule_id="repo-empty"
        )
        res = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=AnalysisSummary(total_findings=1, findings_by_severity={"info": 1}),
            findings=[finding]
        )

        # Determinism check
        opt1 = self.engine.generate_recommendations(res)
        opt2 = self.engine.generate_recommendations(res)
        self.assertEqual(opt1, opt2)

        # Thread safety stress test
        def run_rec():
            return self.engine.generate_recommendations(res)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_rec) for _ in range(20)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r, opt1)


if __name__ == "__main__":
    unittest.main()
