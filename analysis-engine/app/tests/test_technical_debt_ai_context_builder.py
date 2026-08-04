"""Unit tests for the Technical Debt AI Context Builder."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone

from app.ai_service.context import AIContextManager
from app.technical_debt import (
    TechnicalDebtCategory,
    TechnicalDebtSeverity,
    TechnicalDebtItem,
    TechnicalDebtSummary,
    TechnicalDebtReport,
    TechnicalDebtAIContextBuilder,
)


class TestTechnicalDebtAIContextBuilder(unittest.TestCase):
    """Verifies populated DTO translation mapping, summary listings, determinism, and concurrency."""

    def setUp(self) -> None:
        self.manager = AIContextManager()
        self.builder = TechnicalDebtAIContextBuilder(self.manager)
        self.time_utc = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)

        self.item1 = TechnicalDebtItem(
            id="debt-1",
            category=TechnicalDebtCategory.CODE_SMELL,
            severity=TechnicalDebtSeverity.MEDIUM,
            title="Smell A",
            effort_minutes=15,
            location_file="src/utils.py",
            location_line=10,
        )
        self.item2 = TechnicalDebtItem(
            id="debt-2",
            category=TechnicalDebtCategory.DUPLICATION,
            severity=TechnicalDebtSeverity.HIGH,
            title="Duplication B",
            effort_minutes=30,
            location_file="src/main.py",
            location_line=40,
        )

        self.summary = TechnicalDebtSummary(
            total_items=2,
            total_effort_minutes=45,
            items_by_category={
                TechnicalDebtCategory.CODE_SMELL: 1,
                TechnicalDebtCategory.DUPLICATION: 1,
            },
            effort_by_severity={
                TechnicalDebtSeverity.MEDIUM: 15,
                TechnicalDebtSeverity.HIGH: 30,
            },
            metadata={"weighted_overall_score": 15.0},
        )

        self.report = TechnicalDebtReport(
            project_name="DebtProj",
            generated_at=self.time_utc,
            items=(self.item1, self.item2),
            summary=self.summary,
        )

    def test_constructor_validation(self) -> None:
        """Verifies constructor validation rejects None managers."""
        with self.assertRaises(ValueError):
            TechnicalDebtAIContextBuilder(None)  # type: ignore

    def test_empty_report_mapping(self) -> None:
        """Verifies builder gracefully maps empty technical debt reports."""
        empty_report = TechnicalDebtReport(
            project_name="EmptyProj",
            generated_at=self.time_utc,
            items=(),
            summary=TechnicalDebtSummary(
                total_items=0,
                total_effort_minutes=0,
                items_by_category={},
                effort_by_severity={},
            ),
        )
        context = self.builder.build_context(empty_report)

        self.assertEqual(context.title, "Technical Debt Context: EmptyProj")
        self.assertEqual(context.metadata["total_items"], 0)
        self.assertEqual(context.metadata["total_effort_minutes"], 0)

    def test_populated_report_mapping(self) -> None:
        """Verifies metadata values, category groups, and sections content preserves."""
        context = self.builder.build_context(self.report)

        # Metadata checks
        self.assertEqual(context.metadata["project_name"], "DebtProj")
        self.assertEqual(context.metadata["total_items"], 2)
        self.assertEqual(context.metadata["total_effort_minutes"], 45)
        self.assertEqual(context.metadata["weighted_overall_score"], 15.0)

        # Sections checks
        sections_map = {sec.name: sec.content for sec in context.sections}
        self.assertIn("Summary", sections_map)
        self.assertIn("Technical Debt Findings", sections_map)
        self.assertIn("Debt Categories", sections_map)
        self.assertIn("Remediation Overview", sections_map)
        self.assertIn("Recommendations Input", sections_map)

        # Content validations
        self.assertIn("Total Technical Debt Items: 2", sections_map["Summary"])
        self.assertIn("- ID: debt-2", sections_map["Technical Debt Findings"])
        self.assertIn("code_smell: 1 items", sections_map["Debt Categories"])
        self.assertIn("HIGH: 30 minutes", sections_map["Remediation Overview"])
        self.assertIn("Technical debt recommendations input requested for overall score 15.00", sections_map["Recommendations Input"])

    def test_deterministic_ordering(self) -> None:
        """Verifies compiled layout mapping outputs remain deterministic."""
        c1 = self.builder.build_context(self.report)
        c2 = self.builder.build_context(self.report)

        self.assertEqual(c1.title, c2.title)
        self.assertEqual(c1.metadata, c2.metadata)
        self.assertEqual(len(c1.sections), len(c2.sections))
        for s1, s2 in zip(c1.sections, c2.sections):
            self.assertEqual(s1.name, s2.name)
            self.assertEqual(s1.content, s2.content)

    def test_report_immutability(self) -> None:
        """Verifies builder does not alter input report attributes."""
        orig_name = self.report.project_name
        _ = self.builder.build_context(self.report)
        self.assertEqual(self.report.project_name, orig_name)

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety mappings under high concurrent calls load."""
        def run_build():
            return self.builder.build_context(self.report)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_build) for _ in range(30)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.title, "Technical Debt Context: DebtProj")
            self.assertEqual(res.metadata["total_effort_minutes"], 45)


if __name__ == "__main__":
    unittest.main()
