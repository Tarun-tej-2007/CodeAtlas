"""Unit tests for the GovernanceViolationAnalyzer and enriched diagnostics validations."""

import unittest
import uuid
from datetime import datetime, timezone

from app.governance import (
    EnrichedViolation,
    GovernanceViolationReport,
    GovernanceValidationError,
    GovernanceViolationAnalyzer,
    PolicyViolation,
    ViolationSeverity,
)


class TestViolationAnalyzer(unittest.TestCase):
    """Verifies severity scaling, priority tiers, root causes, remediations, and reporting groupings."""

    def setUp(self) -> None:
        self.analyzer = GovernanceViolationAnalyzer()
        self.project_id = uuid.uuid4()
        self.commit_id = "commit-xyz-987"
        self.rule_id = uuid.uuid4()

    def test_empty_violation_collections(self) -> None:
        """Verifies report can be compiled with no violation inputs."""
        report = self.analyzer.analyze_violations(
            project_id=self.project_id,
            commit_id=self.commit_id,
            violations=(),
        )
        self.assertEqual(report.project_id, self.project_id)
        self.assertEqual(len(report.violations), 0)
        self.assertEqual(len(report.violations_by_rule), 0)

    def test_severity_refinement_escalation(self) -> None:
        """Verifies severity refinement escalates to ERROR or WARNING for high-risk profiles."""
        v = PolicyViolation(
            rule_id=self.rule_id,
            rule_name="forbidden_import_rule",
            severity=ViolationSeverity.WARNING,
            message="Forbidden import link detected.",
            details={},
        )
        report = self.analyzer.analyze_violations(
            project_id=self.project_id,
            commit_id=self.commit_id,
            violations=(v,),
        )
        # Escalated from WARNING to ERROR because rule name has "forbidden"
        self.assertEqual(report.violations[0].refined_severity, ViolationSeverity.ERROR)

    def test_priority_calculation_tiers(self) -> None:
        """Verifies priority score and priority tier classifications."""
        v1 = PolicyViolation(
            rule_id=self.rule_id,
            rule_name="coupling_rule",
            severity=ViolationSeverity.ERROR,
            message="High coupling detected.",
            details={},
        )
        v2 = PolicyViolation(
            rule_id=self.rule_id,
            rule_name="naming_rule",
            severity=ViolationSeverity.INFO,
            message="Naming deviation.",
            details={},
        )

        report = self.analyzer.analyze_violations(
            project_id=self.project_id,
            commit_id=self.commit_id,
            violations=(v1, v2),
        )

        # coupling rule refined to ERROR: base 80 + 10 = 90 (HIGH)
        self.assertEqual(report.violations[0].priority_tier, "HIGH")
        self.assertEqual(report.violations[0].priority_score, 90.0)

        # naming rule refined to INFO: base 20 - 5 = 15 (LOW)
        self.assertEqual(report.violations[1].priority_tier, "LOW")
        self.assertEqual(report.violations[1].priority_score, 15.0)

    def test_root_cause_and_remediation(self) -> None:
        """Verifies root cause categorization and suggestion generation."""
        v = PolicyViolation(
            rule_id=self.rule_id,
            rule_name="complexity_rule",
            severity=ViolationSeverity.WARNING,
            message="Complexity exceeded limit.",
            details={},
        )
        report = self.analyzer.analyze_violations(
            project_id=self.project_id,
            commit_id=self.commit_id,
            violations=(v,),
        )
        self.assertEqual(report.violations[0].root_cause, "complexity_threshold_exceeded")
        self.assertIn("Deconstruct functions", report.violations[0].suggested_remediation)

    def test_impact_scope_determination(self) -> None:
        """Verifies impact scope is classified from violation details context keys."""
        # Source and Target present -> module_to_module_link
        v1 = PolicyViolation(
            rule_id=self.rule_id,
            rule_name="dependency_rule",
            severity=ViolationSeverity.ERROR,
            message="Illegal dependency.",
            details={"source": "a.py", "target": "b.py"},
        )
        # Only Node ID present -> individual_module
        v2 = PolicyViolation(
            rule_id=self.rule_id,
            rule_name="naming_rule",
            severity=ViolationSeverity.WARNING,
            message="Invalid name.",
            details={"node_id": "c.py"},
        )

        report = self.analyzer.analyze_violations(
            project_id=self.project_id,
            commit_id=self.commit_id,
            violations=(v1, v2),
        )
        self.assertEqual(report.violations[0].impact_scope, "module_to_module_link")
        self.assertEqual(report.violations[1].impact_scope, "individual_module")

    def test_policy_grouping_and_ordering(self) -> None:
        """Verifies violations group by rule name and sort alphabetically."""
        v1 = PolicyViolation(
            rule_id=self.rule_id,
            rule_name="Z_Rule",
            severity=ViolationSeverity.ERROR,
            message="Z Message.",
            details={},
        )
        v2 = PolicyViolation(
            rule_id=self.rule_id,
            rule_name="A_Rule",
            severity=ViolationSeverity.WARNING,
            message="A Message.",
            details={},
        )

        report = self.analyzer.analyze_violations(
            project_id=self.project_id,
            commit_id=self.commit_id,
            violations=(v1, v2),
        )

        # Sorted alphabetically by rule name
        names = [v.rule_name for v in report.violations]
        self.assertEqual(names, ["A_Rule", "Z_Rule"])

        # Group keys sorted alphabetically
        group_keys = list(report.violations_by_rule.keys())
        self.assertEqual(group_keys, ["A_Rule", "Z_Rule"])

    def test_validation_failures_invalid_params(self) -> None:
        """Verifies validation failures for invalid inputs."""
        # None project_id
        with self.assertRaises(GovernanceValidationError):
            self.analyzer.analyze_violations(project_id=None, commit_id="c1", violations=())

        # Empty commit_id
        with self.assertRaises(GovernanceValidationError):
            self.analyzer.analyze_violations(project_id=self.project_id, commit_id=" ", violations=())


if __name__ == "__main__":
    unittest.main()
