"""Unit tests for the Architecture Analysis domain foundation."""

import unittest
from datetime import datetime, timezone
from types import MappingProxyType
from pydantic import ValidationError

from app.architecture_analysis import (
    ArchitectureRuleType,
    ArchitectureSeverity,
    ArchitectureAnalysisError,
    ArchitectureRuleError,
    ArchitectureIssue,
    ArchitectureSummary,
    ArchitectureReport,
    ArchitectureAnalyzer,
)


class MockArchitectureAnalyzer(ArchitectureAnalyzer):
    """Mock implementation of the ArchitectureAnalyzer interface for testing."""

    def analyze(self, *args, **kwargs) -> ArchitectureReport:
        summary = ArchitectureSummary(
            total_issues=1,
            info_count=0,
            low_count=0,
            medium_count=1,
            high_count=0,
            critical_count=0,
        )
        issue = ArchitectureIssue(
            id="issue-1",
            rule_type=ArchitectureRuleType.CIRCULAR_DEPENDENCY,
            severity=ArchitectureSeverity.MEDIUM,
            title="Circular Dependency Test",
            description="Circular dependency detected between modules.",
            affected_symbols=("moduleA", "moduleB"),
            metadata={"cycle_length": 2},
        )
        return ArchitectureReport(
            project_name="TestProject",
            generated_at=datetime.now(timezone.utc),
            issues=(issue,),
            summary=summary,
        )


class TestArchitectureAnalysisDomain(unittest.TestCase):
    """Unit tests for enums, exceptions, and Pydantic models in the architecture analysis domain."""

    def test_enums(self) -> None:
        """Verifies enum value mappings."""
        self.assertEqual(ArchitectureSeverity.CRITICAL, "critical")
        self.assertEqual(ArchitectureRuleType.CIRCULAR_DEPENDENCY, "circular_dependency")
        self.assertEqual(ArchitectureRuleType.LAYER_VIOLATION, "layer_violation")
        self.assertEqual(ArchitectureRuleType.GOD_CLASS, "god_class")

    def test_exceptions_hierarchy(self) -> None:
        """Verifies custom domain exception hierarchy."""
        with self.assertRaises(ArchitectureAnalysisError):
            raise ArchitectureRuleError("Invalid layer definition")

    def test_architecture_issue_immutability_and_validation(self) -> None:
        """Verifies ArchitectureIssue model validation and metadata runtime immutability."""
        issue = ArchitectureIssue(
            id="iss-1",
            rule_type=ArchitectureRuleType.LAYER_VIOLATION,
            severity=ArchitectureSeverity.HIGH,
            title="Layer Violation",
            description="Presentation layer violates layering rule.",
            affected_symbols=("src/ui.py", "src/db.py"),
            metadata={"reason": "direct db import"},
        )

        # Assert property access
        self.assertEqual(issue.id, "iss-1")
        self.assertEqual(issue.metadata["reason"], "direct db import")

        # Assert frozen model (immutability)
        with self.assertRaises((ValidationError, TypeError)):
            issue.id = "iss-2"  # type: ignore

        # Assert metadata is wrapped in MappingProxyType
        self.assertIsInstance(issue.metadata, MappingProxyType)
        with self.assertRaises(TypeError):
            issue.metadata["reason"] = "something else"  # type: ignore

    def test_architecture_summary_model(self) -> None:
        """Verifies ArchitectureSummary field validations."""
        summary = ArchitectureSummary(
            total_issues=5,
            info_count=1,
            low_count=1,
            medium_count=1,
            high_count=1,
            critical_count=1,
        )
        self.assertEqual(summary.total_issues, 5)

        # Assert negative counts raise ValidationError
        with self.assertRaises(ValidationError):
            ArchitectureSummary(
                total_issues=-1,
                info_count=0,
                low_count=0,
                medium_count=0,
                high_count=0,
                critical_count=0,
            )

    def test_architecture_report_timezone_validation(self) -> None:
        """Verifies timezone validation for report timestamp."""
        summary = ArchitectureSummary(
            total_issues=0,
            info_count=0,
            low_count=0,
            medium_count=0,
            high_count=0,
            critical_count=0,
        )

        # Aware UTC timestamp is valid
        valid_now = datetime.now(timezone.utc)
        report = ArchitectureReport(
            project_name="Demo",
            generated_at=valid_now,
            issues=(),
            summary=summary,
        )
        self.assertEqual(report.project_name, "Demo")

        # Naive datetime is invalid
        naive_now = datetime.now()
        with self.assertRaises(ValidationError):
            ArchitectureReport(
                project_name="Demo",
                generated_at=naive_now,
                issues=(),
                summary=summary,
            )

    def test_analyzer_interface_and_mock(self) -> None:
        """Verifies abstract interface contract via mock subclass execution."""
        analyzer = MockArchitectureAnalyzer()
        report = analyzer.analyze()
        self.assertEqual(report.project_name, "TestProject")
        self.assertEqual(len(report.issues), 1)
        self.assertEqual(report.issues[0].rule_type, ArchitectureRuleType.CIRCULAR_DEPENDENCY)

    def test_deterministic_behavior(self) -> None:
        """Verifies model equality and deterministic output structures."""
        summary1 = ArchitectureSummary(
            total_issues=1, info_count=0, low_count=0, medium_count=1, high_count=0, critical_count=0
        )
        summary2 = ArchitectureSummary(
            total_issues=1, info_count=0, low_count=0, medium_count=1, high_count=0, critical_count=0
        )
        self.assertEqual(summary1, summary2)

        fixed_time = datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)
        issue1 = ArchitectureIssue(
            id="iss-1",
            rule_type=ArchitectureRuleType.HIGH_COMPLEXITY,
            severity=ArchitectureSeverity.LOW,
            title="Complex Function",
            description="Highly complex code detected.",
            affected_symbols=("func_a",),
            metadata={"score": 15},
        )
        issue2 = ArchitectureIssue(
            id="iss-1",
            rule_type=ArchitectureRuleType.HIGH_COMPLEXITY,
            severity=ArchitectureSeverity.LOW,
            title="Complex Function",
            description="Highly complex code detected.",
            affected_symbols=("func_a",),
            metadata={"score": 15},
        )

        report1 = ArchitectureReport(
            project_name="ProjectAlpha",
            generated_at=fixed_time,
            issues=(issue1,),
            summary=summary1,
        )
        report2 = ArchitectureReport(
            project_name="ProjectAlpha",
            generated_at=fixed_time,
            issues=(issue2,),
            summary=summary2,
        )
        self.assertEqual(report1, report2)


if __name__ == "__main__":
    unittest.main()
