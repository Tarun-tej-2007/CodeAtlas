"""Unit tests for the Prompt Context Builder."""

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
    PromptContextSection,
    PromptContext,
    PromptContextBuilder,
)


class TestPromptContextBuilder(unittest.TestCase):
    """Verifies LLM-ready prompt context packaging, ordering, deduplication, and thread safety."""

    def setUp(self) -> None:
        self.builder = PromptContextBuilder()
        self.summary = AnalysisSummary(
            total_findings=2,
            findings_by_severity={"warning": 2},
            duration_ms=100,
            metadata={"unique_files_affected": "1"}
        )
        self.finding1 = AnalysisFinding(
            id="f-1", title="S1", description="Desc 1", severity=AnalysisSeverity.WARNING,
            file_path="src/main.py", start_line=1, end_line=1, rule_id="rule-a"
        )
        self.rec1 = AnalysisRecommendation(
            id="rec-1", finding_id="f-1", remediation="Fix S1", status=RecommendationStatus.OPEN,
            metadata={"priority": "high"}
        )

        self.result = AnalysisResult(
            id="run-123",
            analysis_type=AnalysisType.DESIGN,
            summary=self.summary,
            findings=[self.finding1],
            recommendations=[self.rec1],
            diagnostics=["Step 1"],
            metadata={}
        )

        self.report = AnalysisReport(
            id="rep-123",
            result_id="run-123",
            sections=[
                ReportSection(id="sec-summary", title="Summary Title", content="Raw summary content", metadata={}),
                ReportSection(id="sec-findings", title="Findings Title", content="Raw findings content", metadata={})
            ],
            metadata={}
        )

    def test_empty_inputs(self) -> None:
        context = self.builder.build_prompt_context(report=None, result=None)
        self.assertEqual(context.sections, [])
        self.assertIn("prompt-context-", context.id)

    def test_populated_contexts_and_inclusion(self) -> None:
        context = self.builder.build_prompt_context(report=self.report, result=self.result, granularity="detailed")

        # Sections: summary-context (priority 1), findings-context (priority 2), recs-context (priority 2), report-sec-sec-summary (priority 3), report-sec-sec-findings (priority 3)
        self.assertEqual(len(context.sections), 5)

        # Priority 1: summary-context
        self.assertEqual(context.sections[0].id, "summary-context")
        self.assertEqual(context.sections[0].priority, 1)
        self.assertIn("Total Findings: 2", context.sections[0].content)

        # Priority 2: findings-context, recs-context (sorted alphabetically by ID)
        self.assertEqual(context.sections[1].id, "findings-context")
        self.assertEqual(context.sections[2].id, "recs-context")
        self.assertIn("Desc 1", context.sections[1].content)
        self.assertIn("Fix S1", context.sections[2].content)

        # Priority 3: report-sec-sec-findings, report-sec-sec-summary (sorted alphabetically by ID)
        self.assertEqual(context.sections[3].id, "report-sec-sec-findings")
        self.assertEqual(context.sections[4].id, "report-sec-sec-summary")

    def test_compact_granularity(self) -> None:
        context = self.builder.build_prompt_context(report=None, result=self.result, granularity="compact")

        self.assertEqual(len(context.sections), 3)  # summary, findings, recs
        # In compact mode, we omit detailed description or severity dictionary outputs
        self.assertNotIn("Severity Tallies", context.sections[0].content)
        self.assertNotIn("Desc 1", context.sections[1].content)

    def test_serialization_and_immutability(self) -> None:
        context = self.builder.build_prompt_context(report=self.report, result=self.result)

        # Immutability
        with self.assertRaises((ValidationError, TypeError)):
            context.sections = []  # type: ignore

        # Serialization
        dump = context.model_dump()
        self.assertEqual(dump["metadata"]["granularity"], "detailed")
        self.assertEqual(len(dump["sections"]), 5)

        json_str = context.model_dump_json()
        self.assertIn("prompt-context-", json_str)

    def test_repeated_execution_and_concurrency(self) -> None:
        # Determinism check
        c1 = self.builder.build_prompt_context(report=self.report, result=self.result)
        c2 = self.builder.build_prompt_context(report=self.report, result=self.result)
        self.assertEqual(c1, c2)

        # Thread safety stress test
        def run_build():
            return self.builder.build_prompt_context(report=self.report, result=self.result)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_build) for _ in range(20)]
            results = [f.result() for f in futures]

        for context in results:
            self.assertEqual(context, c1)


if __name__ == "__main__":
    unittest.main()
