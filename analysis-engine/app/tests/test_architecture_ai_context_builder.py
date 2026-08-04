"""Unit tests for the ArchitectureAIContextBuilder component."""

import unittest
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.ai_service.context import AIContext, AIContextManager, ContextSection
from app.architecture_analysis import (
    ArchitectureRuleType,
    ArchitectureSeverity,
    ArchitectureIssue,
    ArchitectureSummary,
    ArchitectureReport,
    ArchitectureAIContextBuilder,
)


class TestArchitectureAIContextBuilder(unittest.TestCase):
    """Verifies DTO translation mapping, section order preservation, metadata values, and mock delegation."""

    def setUp(self) -> None:
        self.ai_context_manager = MagicMock(spec=AIContextManager)

        # Real create_context implementation to allow inspection of returned AIContext DTO
        def mock_create_context(title, description, metadata, sections):
            return AIContext(
                title=title,
                description=description,
                metadata=metadata,
                sections=tuple(sections),
            )

        self.ai_context_manager.create_context.side_effect = mock_create_context

        self.builder = ArchitectureAIContextBuilder(self.ai_context_manager)

        # Base fixtures
        self.time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)
        self.summary_empty = ArchitectureSummary(
            total_issues=0,
            info_count=0,
            low_count=0,
            medium_count=0,
            high_count=0,
            critical_count=0,
        )
        self.report_empty = ArchitectureReport(
            project_name="EmptyProj",
            generated_at=self.time,
            issues=(),
            summary=self.summary_empty,
        )

        self.issue_dep = ArchitectureIssue(
            id="iss-dep-1",
            rule_type=ArchitectureRuleType.CIRCULAR_DEPENDENCY,
            severity=ArchitectureSeverity.CRITICAL,
            title="Dependency Cycle",
            description="A -> B -> A",
            affected_symbols=("A", "B"),
            metadata={"cycle_len": 2},
        )
        self.issue_sem = ArchitectureIssue(
            id="iss-sem-1",
            rule_type=ArchitectureRuleType.UNUSED_SYMBOL,
            severity=ArchitectureSeverity.INFO,
            title="Unused Variable",
            description="Variable x is unused",
            affected_symbols=("x",),
            metadata={"file": "test.py"},
        )

        self.summary_populated = ArchitectureSummary(
            total_issues=2,
            info_count=1,
            low_count=0,
            medium_count=0,
            high_count=0,
            critical_count=1,
        )
        self.report_populated = ArchitectureReport(
            project_name="PopulatedProj",
            generated_at=self.time,
            issues=(self.issue_dep, self.issue_sem),
            summary=self.summary_populated,
        )

    def test_empty_report_mapping(self) -> None:
        """Verifies section outputs and empty list handling for report containing zero issues."""
        context = self.builder.build_context(self.report_empty)

        # Assert delegation occurred
        self.ai_context_manager.create_context.assert_called_once()

        self.assertEqual(context.title, "Architecture Analysis Context: EmptyProj")
        self.assertEqual(context.metadata["project_name"], "EmptyProj")
        self.assertEqual(context.metadata["total_issues"], 0)

        # Section counts
        self.assertEqual(len(context.sections), 5)
        names = [sec.name for sec in context.sections]
        self.assertEqual(
            names,
            [
                "Summary",
                "Architecture Issues",
                "Dependency Analysis",
                "Semantic Analysis",
                "Recommendations Input",
            ],
        )

    def test_populated_report_mapping_and_order(self) -> None:
        """Verifies correct section splits for dependency vs semantic violations."""
        context = self.builder.build_context(self.report_populated)

        self.assertEqual(context.metadata["total_issues"], 2)
        self.assertEqual(context.metadata["critical_count"], 1)
        self.assertEqual(context.metadata["info_count"], 1)

        # Verify dependency analysis section
        dep_sec = next(sec for sec in context.sections if sec.name == "Dependency Analysis")
        self.assertIn("iss-dep-1", dep_sec.content)
        self.assertNotIn("iss-sem-1", dep_sec.content)

        # Verify semantic analysis section
        sem_sec = next(sec for sec in context.sections if sec.name == "Semantic Analysis")
        self.assertIn("iss-sem-1", sem_sec.content)
        self.assertNotIn("iss-dep-1", sem_sec.content)

    def test_metadata_generation_correctness(self) -> None:
        """Verifies metadata values match report values exactly."""
        context = self.builder.build_context(self.report_populated)

        expected_meta = {
            "project_name": "PopulatedProj",
            "generated_at": self.time.isoformat(),
            "total_issues": 2,
            "info_count": 1,
            "low_count": 0,
            "medium_count": 0,
            "high_count": 0,
            "critical_count": 1,
        }
        self.assertEqual(dict(context.metadata), expected_meta)

    def test_deterministic_output(self) -> None:
        """Verifies duplicate executions produce identical outputs."""
        ctx1 = self.builder.build_context(self.report_populated)
        ctx2 = self.builder.build_context(self.report_populated)
        self.assertEqual(ctx1, ctx2)

    def test_context_immutability(self) -> None:
        """Verifies fields inside the returned context DTO cannot be modified."""
        context = self.builder.build_context(self.report_populated)

        with self.assertRaises(TypeError):
            context.metadata["project_name"] = "Malicious"  # type: ignore

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safe execution when builder is invoked concurrently."""
        def run_build():
            return self.builder.build_context(self.report_populated)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_build) for _ in range(20)]
            results = [f.result() for f in futures]

        for r in results:
            self.assertEqual(r.metadata["project_name"], "PopulatedProj")
            self.assertEqual(len(r.sections), 5)


if __name__ == "__main__":
    unittest.main()
