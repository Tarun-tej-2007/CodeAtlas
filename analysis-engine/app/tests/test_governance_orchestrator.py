"""Unit tests for the GovernanceService orchestrator."""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.governance.enums import GovernanceStatus, ViolationSeverity
from app.governance.exceptions import (
    GovernanceError,
    GovernanceValidationError,
    PolicyEvaluationError,
)
from app.governance.interfaces import (
    ComplianceScorer,
    GovernancePersistence,
    PolicyRuleEvaluator,
    ViolationAnalyzer,
)
from app.governance.models import (
    ComplianceReport,
    ComplianceScore,
    EnrichedViolation,
    GovernanceAnalysisResult,
    GovernancePolicy,
    GovernanceRequest,
    GovernanceResult,
    GovernanceSummary,
    GovernanceViolationReport,
    PolicyMetadata,
    PolicyRule,
    PolicyViolation,
)
from app.governance.service import GovernanceService


class TestGovernanceOrchestrator(unittest.TestCase):
    """Verifies orchestration flow of GovernanceService including success, short-circuit, and error states."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.commit_id = "commit-abc-123"
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)

        # Mocks for constructor DI
        self.policy_evaluator = MagicMock(spec=PolicyRuleEvaluator)
        self.violation_analyzer = MagicMock(spec=ViolationAnalyzer)
        self.compliance_scorer = MagicMock(spec=ComplianceScorer)
        self.persistence = MagicMock(spec=GovernancePersistence)

        # Instantiate service
        self.service = GovernanceService(
            policy_evaluator=self.policy_evaluator,
            violation_analyzer=self.violation_analyzer,
            compliance_scorer=self.compliance_scorer,
            persistence=self.persistence,
        )

        # Setup basic mock DTO structures
        self.policy_meta = PolicyMetadata(
            name="Layer Boundary Policy",
            version="1.0.0",
            category="layer",
            created_at=self.time_utc,
        )
        self.policy_rule = PolicyRule(
            name="No UI to DB import",
            rule_type="layer_ordering",
            severity=ViolationSeverity.ERROR,
            configuration={"allowed_layer_dependencies": {"UI": ()}},
        )
        self.policy = GovernancePolicy(
            metadata=self.policy_meta,
            rules=(self.policy_rule,),
        )
        self.request = GovernanceRequest(
            project_id=self.project_id,
            project_name="Atlas",
            commit_id=self.commit_id,
            policies=(self.policy,),
        )

    def test_constructor_dependency_injection_validation(self) -> None:
        """Verifies constructor dependency injection rejects None or invalid types."""
        with self.assertRaises(ValueError):
            GovernanceService(None, self.violation_analyzer, self.compliance_scorer)
        with self.assertRaises(ValueError):
            GovernanceService(self.policy_evaluator, None, self.compliance_scorer)
        with self.assertRaises(ValueError):
            GovernanceService(self.policy_evaluator, self.violation_analyzer, None)

        with self.assertRaises(TypeError):
            GovernanceService("invalid", self.violation_analyzer, self.compliance_scorer)
        with self.assertRaises(TypeError):
            GovernanceService(self.policy_evaluator, "invalid", self.compliance_scorer)
        with self.assertRaises(TypeError):
            GovernanceService(self.policy_evaluator, self.violation_analyzer, "invalid")
        with self.assertRaises(TypeError):
            GovernanceService(
                self.policy_evaluator,
                self.violation_analyzer,
                self.compliance_scorer,
                persistence="invalid",
            )

    def test_validation_failures_null_or_invalid_request(self) -> None:
        """Verifies verify_governance raises GovernanceValidationError on invalid requests."""
        with self.assertRaises(GovernanceValidationError):
            self.service.verify_governance(None)
        with self.assertRaises(GovernanceValidationError):
            self.service.verify_governance("not-a-request")

        # Invalid policy type inside request policies list
        mock_req = MagicMock(spec=GovernanceRequest)
        mock_req.project_id = self.project_id
        mock_req.commit_id = self.commit_id
        mock_req.policies = ("not-a-policy",)
        with self.assertRaises(GovernanceValidationError):
            self.service.verify_governance(mock_req)

    def test_empty_policy_workflow_and_short_circuit(self) -> None:
        """Verifies short-circuit path when the request has no policies or no violations."""
        req_empty = GovernanceRequest(
            project_id=self.project_id,
            project_name="Atlas",
            commit_id=self.commit_id,
            policies=(),
        )

        eval_result = GovernanceResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            status=GovernanceStatus.PASSED,
            violations=(),
            summary=GovernanceSummary(passed_count=0, failed_count=0, warning_count=0, total_rules=0),
            created_at=self.time_utc,
        )
        self.policy_evaluator.evaluate_request.return_value = eval_result

        # Compliance Scorer setup
        comp_score = ComplianceScore(
            overall_score=100.0,
            category_scores={},
            repository_score=100.0,
            policy_coverage=100.0,
        )
        comp_report = ComplianceReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            compliance_score=comp_score,
            violation_report_id=uuid.uuid4(),
        )
        self.compliance_scorer.calculate_compliance.return_value = comp_report

        res = self.service.verify_governance(req_empty)

        # Assertions
        self.assertEqual(res.status, GovernanceStatus.PASSED)
        self.assertEqual(res.evaluation_result, eval_result)
        self.assertEqual(len(res.violation_report.violations), 0)
        self.assertEqual(res.compliance_report, comp_report)

        # Verify downstream components
        self.policy_evaluator.evaluate_request.assert_called_once_with(req_empty)
        # Should short-circuit violation analyzer
        self.violation_analyzer.analyze_violations.assert_not_called()
        self.compliance_scorer.calculate_compliance.assert_called_once()
        self.persistence.save_result.assert_called_once_with(eval_result)

    def test_single_policy_with_violations_workflow(self) -> None:
        """Verifies complete workflow execution for a single policy with one violation."""
        raw_violation = PolicyViolation(
            rule_id=self.policy_rule.rule_id,
            rule_name=self.policy_rule.name,
            severity=ViolationSeverity.ERROR,
            message="UI imports DB.",
            details={},
        )
        eval_result = GovernanceResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            status=GovernanceStatus.FAILED,
            violations=(raw_violation,),
            summary=GovernanceSummary(passed_count=0, failed_count=1, warning_count=0, total_rules=1),
            created_at=self.time_utc,
        )
        self.policy_evaluator.evaluate_request.return_value = eval_result

        enriched = EnrichedViolation(
            rule_id=self.policy_rule.rule_id,
            rule_name=self.policy_rule.name,
            original_severity=ViolationSeverity.ERROR,
            refined_severity=ViolationSeverity.ERROR,
            priority_score=90.0,
            priority_tier="HIGH",
            root_cause="layer_boundary_bypass",
            impact_scope="layer_to_layer_link",
            suggested_remediation="Refactor.",
            original_message="UI imports DB.",
            details={},
        )
        violation_report = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            violations=(enriched,),
            violations_by_rule={self.policy_rule.name: (enriched,)},
            violations_by_severity={ViolationSeverity.ERROR.value: 1},
        )
        self.violation_analyzer.analyze_violations.return_value = violation_report

        comp_score = ComplianceScore(
            overall_score=85.0,
            category_scores={"layer": 85.0},
            repository_score=95.0,
            policy_coverage=0.0,
        )
        comp_report = ComplianceReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            compliance_score=comp_score,
            violation_report_id=violation_report.report_id,
        )
        self.compliance_scorer.calculate_compliance.return_value = comp_report

        # History list returned by persistence
        self.persistence.list_results.return_value = ()

        res = self.service.verify_governance(self.request)

        # Assertions
        self.assertEqual(res.status, GovernanceStatus.FAILED)
        self.assertEqual(res.evaluation_result, eval_result)
        self.assertEqual(res.violation_report, violation_report)
        self.assertEqual(res.compliance_report, comp_report)

        # Check call trace
        self.policy_evaluator.evaluate_request.assert_called_once_with(self.request)
        self.violation_analyzer.analyze_violations.assert_called_once_with(
            project_id=self.project_id, commit_id=self.commit_id, violations=(raw_violation,)
        )
        self.compliance_scorer.calculate_compliance.assert_called_once_with(
            violation_report=violation_report, history=()
        )
        self.persistence.save_result.assert_called_once_with(eval_result)
        self.persistence.save_violation_report.assert_called_once_with(violation_report)
        self.persistence.save_compliance_report.assert_called_once_with(comp_report)

    def test_policy_evaluation_failure(self) -> None:
        """Verifies policy definition/evaluation failure propagation."""
        self.policy_evaluator.evaluate_request.side_effect = PolicyEvaluationError("Evaluation failed.")

        with self.assertRaises(PolicyEvaluationError):
            self.service.verify_governance(self.request)

        self.violation_analyzer.analyze_violations.assert_not_called()
        self.compliance_scorer.calculate_compliance.assert_not_called()

    def test_violation_analyzer_failure(self) -> None:
        """Verifies violation analyzer runtime exception wrap/propagation."""
        raw_violation = PolicyViolation(
            rule_id=self.policy_rule.rule_id,
            rule_name=self.policy_rule.name,
            severity=ViolationSeverity.ERROR,
            message="UI imports DB.",
            details={},
        )
        eval_result = GovernanceResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            status=GovernanceStatus.FAILED,
            violations=(raw_violation,),
            summary=GovernanceSummary(passed_count=0, failed_count=1, warning_count=0, total_rules=1),
            created_at=self.time_utc,
        )
        self.policy_evaluator.evaluate_request.return_value = eval_result
        self.violation_analyzer.analyze_violations.side_effect = ValueError("Diagnostics error.")

        with self.assertRaises(PolicyEvaluationError):
            self.service.verify_governance(self.request)

        self.compliance_scorer.calculate_compliance.assert_not_called()

    def test_compliance_scorer_failure(self) -> None:
        """Verifies compliance scorer runtime exception wrap/propagation."""
        raw_violation = PolicyViolation(
            rule_id=self.policy_rule.rule_id,
            rule_name=self.policy_rule.name,
            severity=ViolationSeverity.ERROR,
            message="UI imports DB.",
            details={},
        )
        eval_result = GovernanceResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            status=GovernanceStatus.FAILED,
            violations=(raw_violation,),
            summary=GovernanceSummary(passed_count=0, failed_count=1, warning_count=0, total_rules=1),
            created_at=self.time_utc,
        )
        self.policy_evaluator.evaluate_request.return_value = eval_result

        enriched = EnrichedViolation(
            rule_id=self.policy_rule.rule_id,
            rule_name=self.policy_rule.name,
            original_severity=ViolationSeverity.ERROR,
            refined_severity=ViolationSeverity.ERROR,
            priority_score=90.0,
            priority_tier="HIGH",
            root_cause="layer_boundary_bypass",
            impact_scope="layer_to_layer_link",
            suggested_remediation="Refactor.",
            original_message="UI imports DB.",
            details={},
        )
        violation_report = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            violations=(enriched,),
            violations_by_rule={self.policy_rule.name: (enriched,)},
            violations_by_severity={ViolationSeverity.ERROR.value: 1},
        )
        self.violation_analyzer.analyze_violations.return_value = violation_report

        self.compliance_scorer.calculate_compliance.side_effect = RuntimeError("Scoring calculation crash.")

        with self.assertRaises(PolicyEvaluationError):
            self.service.verify_governance(self.request)

    def test_deterministic_repeated_execution(self) -> None:
        """Verifies repeated execution of the orchestrator produces identical matching DTO metrics."""
        raw_violation = PolicyViolation(
            rule_id=self.policy_rule.rule_id,
            rule_name=self.policy_rule.name,
            severity=ViolationSeverity.ERROR,
            message="UI imports DB.",
            details={},
        )
        eval_result = GovernanceResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            status=GovernanceStatus.FAILED,
            violations=(raw_violation,),
            summary=GovernanceSummary(passed_count=0, failed_count=1, warning_count=0, total_rules=1),
            created_at=self.time_utc,
        )
        self.policy_evaluator.evaluate_request.return_value = eval_result

        enriched = EnrichedViolation(
            rule_id=self.policy_rule.rule_id,
            rule_name=self.policy_rule.name,
            original_severity=ViolationSeverity.ERROR,
            refined_severity=ViolationSeverity.ERROR,
            priority_score=90.0,
            priority_tier="HIGH",
            root_cause="layer_boundary_bypass",
            impact_scope="layer_to_layer_link",
            suggested_remediation="Refactor.",
            original_message="UI imports DB.",
            details={},
        )
        violation_report = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            violations=(enriched,),
            violations_by_rule={self.policy_rule.name: (enriched,)},
            violations_by_severity={ViolationSeverity.ERROR.value: 1},
        )
        self.violation_analyzer.analyze_violations.return_value = violation_report

        comp_score = ComplianceScore(
            overall_score=85.0,
            category_scores={"layer": 85.0},
            repository_score=95.0,
            policy_coverage=0.0,
        )
        comp_report = ComplianceReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            compliance_score=comp_score,
            violation_report_id=violation_report.report_id,
        )
        self.compliance_scorer.calculate_compliance.return_value = comp_report
        self.persistence.list_results.return_value = ()

        # Execute multiple times
        res1 = self.service.verify_governance(self.request)
        res2 = self.service.verify_governance(self.request)

        # Assert values match
        self.assertEqual(res1.status, res2.status)
        self.assertEqual(res1.evaluation_result, res2.evaluation_result)
        self.assertEqual(res1.violation_report, res2.violation_report)
        self.assertEqual(res1.compliance_report, res2.compliance_report)


if __name__ == "__main__":
    unittest.main()
