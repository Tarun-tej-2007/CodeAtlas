"""Unit tests for the Unified AI Context Builder."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from types import MappingProxyType

from app.ai_service.context import AIContextManager
from app.unified_analysis import (
    AnalysisStatus,
    UnifiedAnalysisReport,
    UnifiedAIContextBuilder,
)


class TestUnifiedAIContextBuilder(unittest.TestCase):
    """Verifies populated DTO conversion, section determinism, metadata freezing, and concurrency."""

    def setUp(self) -> None:
        self.manager = AIContextManager()
        self.builder = UnifiedAIContextBuilder(self.manager)
        self.time_utc = datetime(2026, 8, 5, 12, 0, 0, tzinfo=timezone.utc)

        self.report = UnifiedAnalysisReport(
            project_name="UnifiedProj",
            generated_at=self.time_utc,
            status=AnalysisStatus.SUCCESS,
            scan_result={"files_scanned": 10},
            parse_result={"files_parsed": 8},
            architecture_result="architecture-ok",
            quality_result=None,
            technical_debt_result={"issues": ["smell-1", "dead-code-2"]},
            metadata={"user_config": "enabled", "run_id": "uuid-123"},
        )

    def test_constructor_validation(self) -> None:
        """Verifies constructor validation rejects None managers."""
        with self.assertRaises(ValueError):
            UnifiedAIContextBuilder(None)  # type: ignore

    def test_empty_report_mapping(self) -> None:
        """Verifies context mapping with empty/default reports."""
        empty_report = UnifiedAnalysisReport(
            project_name="EmptyProj",
            generated_at=self.time_utc,
            status=AnalysisStatus.PENDING,
        )
        context = self.builder.build_context(empty_report)

        self.assertEqual(context.title, "Unified Analysis Context: EmptyProj")
        self.assertEqual(context.metadata["status"], "pending")

        sections_map = {sec.name: sec.content for sec in context.sections}
        self.assertEqual(sections_map["Scan Results"], "No data available.")
        self.assertEqual(sections_map["Architecture Analysis"], "No data available.")

    def test_populated_report_mapping(self) -> None:
        """Verifies populated report aggregates properties, types, and values correctly."""
        context = self.builder.build_context(self.report)

        # Metadata checks
        self.assertEqual(context.metadata["project_name"], "UnifiedProj")
        self.assertEqual(context.metadata["status"], "success")
        self.assertEqual(context.metadata["meta_user_config"], "enabled")
        self.assertEqual(context.metadata["meta_run_id"], "uuid-123")

        # Sections checks
        sections_map = {sec.name: sec.content for sec in context.sections}
        self.assertIn("Repository Summary", sections_map)
        self.assertIn("Scan Results", sections_map)
        self.assertIn("Parse Results", sections_map)
        self.assertIn("Architecture Analysis", sections_map)
        self.assertIn("Quality Analysis", sections_map)
        self.assertIn("Technical Debt Analysis", sections_map)
        self.assertIn("Metadata", sections_map)
        self.assertIn("Recommendations Input", sections_map)

        # Data serialization checks (deterministic ordering)
        self.assertEqual(sections_map["Scan Results"], "files_scanned: 10")
        self.assertEqual(sections_map["Parse Results"], "files_parsed: 8")
        self.assertEqual(sections_map["Architecture Analysis"], "architecture-ok")
        self.assertEqual(sections_map["Quality Analysis"], "No data available.")
        self.assertEqual(
            sections_map["Technical Debt Analysis"],
            "issues: [dead-code-2, smell-1]",
        )
        self.assertIn("user_config: enabled", sections_map["Metadata"])
        self.assertIn("Unified repository analysis review requested for project UnifiedProj", sections_map["Recommendations Input"])

    def test_deterministic_ordering(self) -> None:
        """Verifies context build outputs are deterministic."""
        c1 = self.builder.build_context(self.report)
        c2 = self.builder.build_context(self.report)

        self.assertEqual(c1.title, c2.title)
        self.assertEqual(c1.metadata, c2.metadata)
        self.assertEqual(len(c1.sections), len(c2.sections))
        for s1, s2 in zip(c1.sections, c2.sections):
            self.assertEqual(s1.name, s2.name)
            self.assertEqual(s1.content, s2.content)

    def test_report_immutability(self) -> None:
        """Verifies report is not mutated."""
        orig_name = self.report.project_name
        _ = self.builder.build_context(self.report)
        self.assertEqual(self.report.project_name, orig_name)

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety during parallel context creations."""
        def run_build():
            return self.builder.build_context(self.report)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_build) for _ in range(30)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.title, "Unified Analysis Context: UnifiedProj")
            self.assertEqual(res.metadata["meta_user_config"], "enabled")


if __name__ == "__main__":
    unittest.main()
