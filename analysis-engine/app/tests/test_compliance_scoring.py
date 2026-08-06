"""Unit tests for the ComplianceScoringService and scoring calculations."""

import unittest
import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from pydantic import ValidationError

from app.governance import (
    ComplianceReport,
    ComplianceScore,
    ComplianceScoringService,
    EnrichedViolation,
    GovernanceViolationReport,
    GovernanceValidationError,
    ViolationSeverity,
)


class TestComplianceScoring(unittest.TestCase):
    """Verifies calculations of overall compliance scores, category deductions, and history trends."""

    def setUp(self) -> None:
        self.service = ComplianceScoringService()
        self.project_id = uuid.uuid4()
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)
        self.rule_id = uuid.uuid4()

    def test_empty_violation_report_scoring(self) -> None:
        """Verifies overall and category scores remain 100.0 when no violations exist."""
        violation_report = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id="commit-abc",
            generated_at=self.time_utc,
            violations=(),
            violations_by_rule={},
            violations_by_severity={},
        )
        report = self.service.calculate_compliance(violation_report)

        self.assertEqual(report.compliance_score.overall_score, 100.0)
        self.assertEqual(report.compliance_score.repository_score, 100.0)
        self.assertEqual(report.compliance_score.policy_coverage, 100.0)
        # Check all categories are 100.0
        for cat, score in report.compliance_score.category_scores.items():
            self.assertEqual(score, 100.0)

    def test_single_violation_scoring(self) -> None:
        """Verifies precise deductions are applied for a single violation of ERROR severity."""
        ev = EnrichedViolation(
            violation_id=uuid.uuid4(),
            rule_id=self.rule_id,
            rule_name="coupling_rule",
            original_severity=ViolationSeverity.ERROR,
            refined_severity=ViolationSeverity.ERROR,
            priority_score=90.0,
            priority_tier="HIGH",
            root_cause="high_coupling_detected",
            impact_scope="module_to_module_link",
            suggested_remediation="Decouple.",
            original_message="High coupling.",
            details={},
        )
        violation_report = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id="commit-abc",
            generated_at=self.time_utc,
            violations=(ev,),
            violations_by_rule={"coupling_rule": (ev,)},
            violations_by_severity={ViolationSeverity.ERROR.value: 1},
        )
        report = self.service.calculate_compliance(violation_report)

        # 100.0 - 15.0 (ERROR deduction) = 85.0
        self.assertEqual(report.compliance_score.overall_score, 85.0)
        self.assertEqual(report.compliance_score.category_scores["metric"], 85.0)

        # Others remain 100.0
        self.assertEqual(report.compliance_score.category_scores["dependency"], 100.0)

    def test_category_compliance_multiple_violations(self) -> None:
        """Verifies multiple deductions across different categories are applied correctly."""
        ev1 = EnrichedViolation(
            violation_id=uuid.uuid4(),
            rule_id=self.rule_id,
            rule_name="coupling_rule",
            original_severity=ViolationSeverity.ERROR,
            refined_severity=ViolationSeverity.ERROR,
            priority_score=90.0,
            priority_tier="HIGH",
            root_cause="high_coupling_detected",
            impact_scope="module_to_module_link",
            suggested_remediation="Decouple.",
            original_message="High coupling.",
            details={},
        )
        ev2 = EnrichedViolation(
            violation_id=uuid.uuid4(),
            rule_id=self.rule_id,
            rule_name="naming_rule",
            original_severity=ViolationSeverity.INFO,
            refined_severity=ViolationSeverity.WARNING,
            priority_score=45.0,
            priority_tier="MEDIUM",
            root_cause="naming_convention_deviation",
            impact_scope="individual_module",
            suggested_remediation="Rename.",
            original_message="Bad name.",
            details={},
        )

        violation_report = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id="commit-abc",
            generated_at=self.time_utc,
            violations=(ev1, ev2),
            violations_by_rule={"coupling_rule": (ev1,), "naming_rule": (ev2,)},
            violations_by_severity={
                ViolationSeverity.ERROR.value: 1,
                ViolationSeverity.WARNING.value: 1,
            },
        )
        report = self.service.calculate_compliance(violation_report)

        # Overall: 100 - 15 (ERROR) - 5 (WARNING) = 80.0
        self.assertEqual(report.compliance_score.overall_score, 80.0)
        # Metric category: 100 - 15 = 85.0
        self.assertEqual(report.compliance_score.category_scores["metric"], 85.0)
        # Naming category: 100 - 5 = 95.0
        self.assertEqual(report.compliance_score.category_scores["naming"], 95.0)

    def test_trend_aware_compliance_adjustments(self) -> None:
        """Verifies trend-aware bonus or penalty offsets based on history average."""
        ev = EnrichedViolation(
            violation_id=uuid.uuid4(),
            rule_id=self.rule_id,
            rule_name="coupling_rule",
            original_severity=ViolationSeverity.ERROR,
            refined_severity=ViolationSeverity.ERROR,
            priority_score=90.0,
            priority_tier="HIGH",
            root_cause="high_coupling_detected",
            impact_scope="module_to_module_link",
            suggested_remediation="Decouple.",
            original_message="High coupling.",
            details={},
        )
        violation_report = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id="commit-abc",
            generated_at=self.time_utc,
            violations=(ev,),
            violations_by_rule={"coupling_rule": (ev,)},
            violations_by_severity={ViolationSeverity.ERROR.value: 1},
        )

        # 1. Historical run with MORE violations (e.g. 3 violations) -> Positive Adjustment (+5.0)
        hist_rep = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id="commit-old",
            generated_at=self.time_utc,
            violations=(ev, ev, ev),
            violations_by_rule={},
            violations_by_severity={},
        )
        report_bonus = self.service.calculate_compliance(violation_report, history=(hist_rep,))
        # 100.0 - 15.0 (ERROR) + 5.0 (Bonus) = 90.0
        self.assertEqual(report_bonus.compliance_score.overall_score, 90.0)
        self.assertEqual(report_bonus.compliance_score.trend_adjustment, 5.0)

        # 2. Historical run with NO violations -> Negative Adjustment (-5.0)
        hist_rep_empty = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id="commit-old2",
            generated_at=self.time_utc,
            violations=(),
            violations_by_rule={},
            violations_by_severity={},
        )
        report_penalty = self.service.calculate_compliance(violation_report, history=(hist_rep_empty,))
        # 100.0 - 15.0 (ERROR) - 5.0 (Penalty) = 80.0
        self.assertEqual(report_penalty.compliance_score.overall_score, 80.0)
        self.assertEqual(report_penalty.compliance_score.trend_adjustment, -5.0)

    def test_validation_failures_invalid_params(self) -> None:
        """Verifies calculation fails when passing None report."""
        with self.assertRaises(GovernanceValidationError):
            self.service.calculate_compliance(None)


if __name__ == "__main__":
    unittest.main()
