"""Unit tests for the AI Analysis Summary Engine."""

import unittest
import json
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
    SummaryEngine,
    SummaryMetricCalculator,
)


class CustomTestCalculator(SummaryMetricCalculator):
    """Custom metric calculator to verify extensibility."""

    def calculate(self, result: AnalysisResult) -> dict[str, str]:
        return {"custom_summary_stat": "custom-val"}


class TestSummaryEngine(unittest.TestCase):
    """Verifies aggregate severity tallies, unique file counts, and metadata extensions."""

    def setUp(self) -> None:
        self.engine = SummaryEngine()
        self.empty_summary = AnalysisSummary(total_findings=0, findings_by_severity={}, duration_ms=0)

    def test_empty_analysis(self) -> None:
        res_empty = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=self.empty_summary,
            findings=[],
            recommendations=[]
        )
        res = self.engine.summarize(res_empty)
        self.assertEqual(res.summary.total_findings, 0)
        self.assertEqual(res.summary.findings_by_severity, {})
        self.assertEqual(res.summary.metadata["total_recommendations"], "0")
        self.assertEqual(res.summary.metadata["unique_files_affected"], "0")

    def test_single_finding(self) -> None:
        finding = AnalysisFinding(
            id="f-1",
            title="Smell",
            description="...",
            severity=AnalysisSeverity.WARNING,
            file_path="src/main.py",
            start_line=10,
            end_line=12
        )
        res = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=self.empty_summary,
            findings=[finding],
            recommendations=[]
        )

        res_opt = self.engine.summarize(res)
        self.assertEqual(res_opt.summary.total_findings, 1)
        self.assertEqual(res_opt.summary.findings_by_severity, {"warning": 1})
        self.assertEqual(res_opt.summary.metadata["unique_files_affected"], "1")

    def test_multiple_findings_severity_and_file_aggregations(self) -> None:
        f1 = AnalysisFinding(
            id="f-1", title="S1", description="...", severity=AnalysisSeverity.WARNING,
            file_path="src/main.py", start_line=1, end_line=1
        )
        f2 = AnalysisFinding(
            id="f-2", title="S2", description="...", severity=AnalysisSeverity.CRITICAL,
            file_path="src/utils.py", start_line=2, end_line=2
        )
        f3 = AnalysisFinding(
            id="f-3", title="S3", description="...", severity=AnalysisSeverity.WARNING,
            file_path="src/main.py", start_line=5, end_line=5
        )
        
        # Recommendations
        r1 = AnalysisRecommendation(
            id="rec-1", finding_id="f-1", remediation="Fix S1", status=RecommendationStatus.OPEN
        )

        res = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=self.empty_summary,
            findings=[f1, f2, f3],
            recommendations=[r1]
        )

        res_opt = self.engine.summarize(res)
        self.assertEqual(res_opt.summary.total_findings, 3)
        self.assertEqual(res_opt.summary.findings_by_severity, {"warning": 2, "critical": 1})
        self.assertEqual(res_opt.summary.metadata["total_recommendations"], "1")
        self.assertEqual(res_opt.summary.metadata["unique_files_affected"], "2")  # main.py and utils.py

    def test_extensibility_with_custom_calculator(self) -> None:
        custom_engine = SummaryEngine(calculators=[CustomTestCalculator()])
        res = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=self.empty_summary,
            findings=[]
        )
        res_opt = custom_engine.summarize(res)
        self.assertEqual(res_opt.summary.metadata["custom_summary_stat"], "custom-val")

    def test_serialization_and_immutability(self) -> None:
        res = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=self.empty_summary,
            findings=[]
        )
        res_opt = self.engine.summarize(res)

        # Immutability: assert we cannot modify summary directly
        with self.assertRaises((ValidationError, TypeError)):
            res_opt.summary = self.empty_summary  # type: ignore

        # Serialization
        dump = res_opt.model_dump()
        self.assertEqual(dump["summary"]["total_findings"], 0)
        self.assertEqual(dump["summary"]["metadata"]["total_recommendations"], "0")

    def test_repeated_execution_and_concurrency(self) -> None:
        f1 = AnalysisFinding(
            id="f-1", title="S1", description="...", severity=AnalysisSeverity.WARNING,
            file_path="src/main.py", start_line=1, end_line=1
        )
        res = AnalysisResult(
            id="run-1",
            analysis_type=AnalysisType.DESIGN,
            summary=self.empty_summary,
            findings=[f1]
        )

        opt1 = self.engine.summarize(res)
        opt2 = self.engine.summarize(res)
        self.assertEqual(opt1, opt2)

        def run_summary():
            return self.engine.summarize(res)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_summary) for _ in range(20)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r, opt1)


if __name__ == "__main__":
    unittest.main()
