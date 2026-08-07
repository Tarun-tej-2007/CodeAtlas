"""Unit and integration tests for Governance production hardening."""

import logging
import threading
import time
import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from app.governance.cache import execution_cache
from app.governance.exceptions import (
    GovernanceError,
    GovernancePersistenceError,
    GovernanceValidationError,
    PolicyEvaluationError,
)
from app.governance.enums import GovernanceStatus, ViolationSeverity
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
    PolicyViolation,
)
from app.governance.service import GovernanceService


class TestGovernanceHardening(unittest.TestCase):
    """Verifies timing tracking, correlation propagation, exception translation and context cleanups."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.commit_id = "commit-hardening-123"
        self.correlation_id = "corr-hardening-test-uuid"
        self.time_utc = datetime(2026, 8, 7, 10, 0, 0, tzinfo=timezone.utc)

        # Build mocked sub-engines
        self.evaluator = MagicMock(spec=PolicyRuleEvaluator)
        self.analyzer = MagicMock(spec=ViolationAnalyzer)
        self.scorer = MagicMock(spec=ComplianceScorer)
        self.persistence = MagicMock(spec=GovernancePersistence)

        # Build standard output responses
        self.violations = (
            PolicyViolation(
                rule_id=uuid.uuid4(),
                rule_name="rule1",
                severity=ViolationSeverity.ERROR,
                message="Error 1",
                details={},
            ),
        )
        self.eval_result = GovernanceResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            status=GovernanceStatus.FAILED,
            violations=self.violations,
            summary=GovernanceSummary(
                passed_count=0,
                failed_count=1,
                warning_count=0,
                total_rules=1,
            ),
            created_at=self.time_utc,
        )
        self.violation_report = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            violations=(
                EnrichedViolation(
                    violation_id=uuid.uuid4(),
                    rule_id=self.violations[0].rule_id,
                    rule_name="rule1",
                    original_severity=ViolationSeverity.ERROR,
                    refined_severity=ViolationSeverity.ERROR,
                    priority_score=80.0,
                    priority_tier="HIGH",
                    root_cause="general_governance_violation",
                    impact_scope="codebase_wide",
                    suggested_remediation="Fix it.",
                    original_message="Error 1",
                    details={},
                ),
            ),
            violations_by_rule={},
            violations_by_severity={},
        )
        self.compliance_report = ComplianceReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            compliance_score=ComplianceScore(
                overall_score=85.0,
                category_scores={},
                repository_score=85.0,
                trend_adjustment=0.0,
                policy_coverage=100.0,
            ),
            violation_report_id=self.violation_report.report_id,
        )

        self.evaluator.evaluate_request.return_value = self.eval_result
        self.analyzer.analyze_violations.return_value = self.violation_report
        self.scorer.calculate_compliance.return_value = self.compliance_report

        self.service = GovernanceService(
            policy_evaluator=self.evaluator,
            violation_analyzer=self.analyzer,
            compliance_scorer=self.scorer,
            persistence=self.persistence,
        )

        # Set up a test log interceptor handler
        self.logger = logging.getLogger("analysis-engine.governance")
        self.log_messages = []
        class InterceptHandler(logging.Handler):
            def emit(self, record):
                self.messages.append(record.getMessage())
        self.handler = InterceptHandler()
        self.handler.messages = self.log_messages
        self.logger.addHandler(self.handler)
        self.logger.setLevel(logging.INFO)

    def tearDown(self) -> None:
        self.logger.removeHandler(self.handler)

    def test_verify_governance_success_flow(self) -> None:
        """Verifies overall orchestration succeeds and records execution timings and correlation ID."""
        request = GovernanceRequest(
            project_id=self.project_id,
            project_name="CodeAtlas",
            commit_id=self.commit_id,
            policies=(),
            correlation_id=self.correlation_id,
        )

        result = self.service.verify_governance(request)

        # Assert correct DTO compilation
        self.assertEqual(result.project_id, self.project_id)
        self.assertEqual(result.status, GovernanceStatus.FAILED)

        # Assert timings are logged and included in extra_info
        metrics = result.extra_info.get("metrics")
        self.assertIsNotNone(metrics)
        self.assertIn("policy_evaluation_ms", metrics)
        self.assertIn("violation_analysis_ms", metrics)
        self.assertIn("compliance_scoring_ms", metrics)
        self.assertIn("persistence_ms", metrics)
        self.assertIn("total_ms", metrics)

        # Correlation ID present in extra_info
        self.assertEqual(result.extra_info.get("correlation_id"), self.correlation_id)

        # Logging messages contain correlation ID
        log_str = "".join(self.log_messages)
        self.assertIn(self.correlation_id, log_str)

    def test_cache_cleanup_after_exceptions(self) -> None:
        """Verifies cache context is completely cleaned up and reset even when run fails."""
        self.evaluator.evaluate_request.side_effect = RuntimeError("Evaluation failed crashed.")
        request = GovernanceRequest(
            project_id=self.project_id,
            project_name="CodeAtlas",
            commit_id=self.commit_id,
            policies=(),
            correlation_id=self.correlation_id,
        )

        with self.assertRaises(PolicyEvaluationError):
            self.service.verify_governance(request)

        # Execution cache context must be completely empty/reset to None default outside block
        self.assertIsNone(execution_cache.get())

    def test_persistence_exception_translation(self) -> None:
        """Verifies standard database/disk failures are translated into GovernancePersistenceError."""
        self.persistence.save_result.side_effect = IOError("Connection failed.")
        request = GovernanceRequest(
            project_id=self.project_id,
            project_name="CodeAtlas",
            commit_id=self.commit_id,
            policies=(),
            correlation_id=self.correlation_id,
        )

        with self.assertRaises(GovernancePersistenceError):
            self.service.verify_governance(request)


if __name__ == "__main__":
    unittest.main()
