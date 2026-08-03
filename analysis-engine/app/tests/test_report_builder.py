"""Unit tests for the AI Analysis Report Builder."""

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
    ReportSection,
    AnalysisReport,
    ReportBuilder,
    ReportSectionBuilder,
)


class CustomSectionBuilder(ReportSectionBuilder):
    """Custom section builder to test report builder extensibility."""

    def build_section(self, result: AnalysisResult) -> Optional[ReportSection]:
        return ReportSection(
            id="sec-custom",
            title="Custom Part",
            content="Hello from custom builder",
            metadata={"source": "test"}
        )


class TestReportBuilder(unittest.TestCase):
    """Verifies markdown report section compilation, extensibility, and serialization."""

    def setUp(self) -> None:
        self.builder = ReportBuilder()
        self.summary = AnalysisSummary(
            total_findings=2,
            findings_by_severity={"warning": 2},
            duration_ms=120,
            metadata={"total_recommendations": "1"}
        )
        self.finding1 = AnalysisFinding(
            id="f-1", title="S1", description="Desc 1", severity=AnalysisSeverity.WARNING,
            file_path="src/main.py", start_line=1, end_line=1, rule_id="rule-a"
        )
        self.finding2 = AnalysisFinding(
            id="f-2", title="S2", description="Desc 2", severity=AnalysisSeverity.WARNING,
            file_path="src/utils.py", start_line=10, end_line=10, rule_id="rule-b"
        )
        self.rec1 = AnalysisRecommendation(
            id="rec-1", finding_id="f-1", remediation="Fix S1", status=RecommendationStatus.OPEN,
            metadata={"priority": "high"}
        )

        self.result = AnalysisResult(
            id="run-123",
            analysis_type=AnalysisType.DESIGN,
            summary=self.summary,
            findings=[self.finding1, self.finding2],
            recommendations=[self.rec1],
            diagnostics=["Step 1 complete", "Step 2 complete"],
            metadata={}
        )

    def test_empty_reports(self) -> None:
        empty_res = AnalysisResult(
            id="run-empty",
            analysis_type=AnalysisType.DESIGN,
            summary=AnalysisSummary(total_findings=0, findings_by_severity={}, duration_ms=0),
            findings=[],
            recommendations=[],
            diagnostics=[]
        )
        report = self.builder.build_report(empty_res)
        
        # Only the summary section should be generated, other sections (findings, recs, logs) are omitted when empty
        self.assertEqual(len(report.sections), 1)
        self.assertEqual(report.sections[0].id, "sec-summary")

    def test_populated_reports_and_content_inclusion(self) -> None:
        report = self.builder.build_report(self.result)

        # Should generate all 4 default sections (Summary, Findings, Recommendations, Diagnostics)
        self.assertEqual(len(report.sections), 4)

        # 1. Summary Section Check
        self.assertEqual(report.sections[0].id, "sec-summary")
        self.assertIn("Total Findings**: 2", report.sections[0].content)
        self.assertIn("WARNING*: 2", report.sections[0].content)

        # 2. Findings Section Check
        self.assertEqual(report.sections[1].id, "sec-findings")
        self.assertIn("1. S1 [rule-a]", report.sections[1].content)
        self.assertIn("2. S2 [rule-b]", report.sections[1].content)

        # 3. Recommendations Section Check
        self.assertEqual(report.sections[2].id, "sec-recommendations")
        self.assertIn("Remediation Strategy**: Fix S1", report.sections[2].content)

        # 4. Diagnostics Section Check
        self.assertEqual(report.sections[3].id, "sec-diagnostics")
        self.assertIn("Step 1 complete", report.sections[3].content)

    def test_extensibility_with_custom_builder(self) -> None:
        ext_builder = ReportBuilder(builders=[CustomSectionBuilder()])
        report = ext_builder.build_report(self.result)

        self.assertEqual(len(report.sections), 1)
        self.assertEqual(report.sections[0].id, "sec-custom")
        self.assertEqual(report.sections[0].content, "Hello from custom builder")

    def test_serialization_and_immutability(self) -> None:
        report = self.builder.build_report(self.result)

        # Immutability
        with self.assertRaises((ValidationError, TypeError)):
            report.sections = []  # type: ignore

        # Serialization
        dump = report.model_dump()
        self.assertEqual(dump["result_id"], "run-123")
        self.assertEqual(len(dump["sections"]), 4)

        json_str = report.model_dump_json()
        self.assertIn("report-run-123", json_str)

    def test_repeated_execution_and_concurrency(self) -> None:
        # Determinism check
        r1 = self.builder.build_report(self.result)
        r2 = self.builder.build_report(self.result)
        self.assertEqual(r1, r2)

        # Thread safety stress test
        def run_build():
            return self.builder.build_report(self.result)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_build) for _ in range(20)]
            results = [f.result() for f in futures]

        for report in results:
            self.assertEqual(report, r1)


if __name__ == "__main__":
    unittest.main()
