"""Unit and integration tests for the Architecture Governance Persistence module."""

import threading
import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Tuple

from app.governance import (
    ComplianceReport,
    ComplianceScore,
    EnrichedViolation,
    GovernanceAnalysisResult,
    GovernancePolicy,
    GovernanceRequest,
    GovernanceResult,
    GovernanceStatus,
    GovernanceSummary,
    GovernanceViolationReport,
    PolicyMetadata,
    PolicyRule,
    PolicyViolation,
    RuleType,
    ViolationSeverity,
)
from app.governance.exceptions import GovernancePersistenceError, GovernanceValidationError
from app.governance.persistence import GovernancePersistenceService, GovernanceRepository


class InMemoryGovernanceRepository(GovernanceRepository):
    """Thread-safe, in-memory implementation of GovernanceRepository supporting database error simulation."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._policies: Dict[uuid.UUID, Dict[str, Any]] = {}
        self._results: Dict[uuid.UUID, Dict[str, Any]] = {}
        self._violations: Dict[uuid.UUID, Dict[str, Any]] = {}
        self._compliances: Dict[uuid.UUID, Dict[str, Any]] = {}
        self._analysis_results: Dict[uuid.UUID, Dict[str, Any]] = {}
        self._simulate_failure = False

    def toggle_failure(self, enable: bool) -> None:
        with self._lock:
            self._simulate_failure = enable

    def _check_failure(self) -> None:
        if self._simulate_failure:
            raise RuntimeError("Database connection timed out.")

    def save_policy(self, policy_id: uuid.UUID, policy_data: Dict[str, Any]) -> None:
        self._check_failure()
        with self._lock:
            self._policies[policy_id] = policy_data

    def get_policy(self, policy_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        self._check_failure()
        with self._lock:
            return self._policies.get(policy_id)

    def list_policies(self) -> Tuple[Dict[str, Any], ...]:
        self._check_failure()
        with self._lock:
            return tuple(self._policies[k] for k in sorted(self._policies.keys()))

    def update_policy(self, policy_id: uuid.UUID, policy_data: Dict[str, Any]) -> None:
        self._check_failure()
        with self._lock:
            self._policies[policy_id] = policy_data

    def save_result(self, result_id: uuid.UUID, project_id: uuid.UUID, result_data: Dict[str, Any]) -> None:
        self._check_failure()
        with self._lock:
            self._results[result_id] = result_data

    def get_result(self, result_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        self._check_failure()
        with self._lock:
            return self._results.get(result_id)

    def list_results(self, project_id: uuid.UUID) -> Tuple[Dict[str, Any], ...]:
        self._check_failure()
        with self._lock:
            results = []
            for k in sorted(self._results.keys()):
                item = self._results[k]
                if str(item.get("project_id")) == str(project_id):
                    results.append(item)
            return tuple(results)

    def save_violation_report(self, report_id: uuid.UUID, report_data: Dict[str, Any]) -> None:
        self._check_failure()
        with self._lock:
            self._violations[report_id] = report_data

    def get_violation_report(self, report_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        self._check_failure()
        with self._lock:
            return self._violations.get(report_id)

    def save_compliance_report(self, report_id: uuid.UUID, report_data: Dict[str, Any]) -> None:
        self._check_failure()
        with self._lock:
            self._compliances[report_id] = report_data

    def get_compliance_report(self, report_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        self._check_failure()
        with self._lock:
            return self._compliances.get(report_id)

    def save_analysis_result(self, result_id: uuid.UUID, result_data: Dict[str, Any]) -> None:
        self._check_failure()
        with self._lock:
            self._analysis_results[result_id] = result_data

    def get_analysis_result(self, result_id: uuid.UUID) -> Optional[Dict[str, Any]]:
        self._check_failure()
        with self._lock:
            return self._analysis_results.get(result_id)


class TestGovernancePersistence(unittest.TestCase):
    """Verifies DTO save/retrieve operations, policy updates, serialization/deserialization, and exception mapping."""

    def setUp(self) -> None:
        self.repo = InMemoryGovernanceRepository()
        self.service = GovernancePersistenceService(self.repo)
        self.project_id = uuid.uuid4()
        self.commit_id = "commit-abc-123"
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)

        # Standard Policy fixture
        self.meta = PolicyMetadata(
            name="Structural Layer Constraint",
            version="1.0.0",
            category="layer",
            created_at=self.time_utc,
        )
        self.rule = PolicyRule(
            name="No ui to db",
            rule_type=RuleType.LAYER_ORDERING,
            severity=ViolationSeverity.ERROR,
            configuration={"allowed": ("utils",)},
        )
        self.policy = GovernancePolicy(
            metadata=self.meta,
            rules=(self.rule,),
        )

        # Result fixture
        self.violation = PolicyViolation(
            rule_id=self.rule.rule_id,
            rule_name=self.rule.name,
            severity=ViolationSeverity.ERROR,
            message="UI refers to DB.",
        )
        self.result = GovernanceResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            status=GovernanceStatus.FAILED,
            violations=(self.violation,),
            summary=GovernanceSummary(passed_count=0, failed_count=1, warning_count=0, total_rules=1),
            created_at=self.time_utc,
        )

    def test_constructor_validation(self) -> None:
        """Verifies constructor parameters validations."""
        with self.assertRaises(ValueError):
            GovernancePersistenceService(None)  # type: ignore
        with self.assertRaises(TypeError):
            GovernancePersistenceService("invalid_repo")  # type: ignore

    def test_save_and_retrieve_policy(self) -> None:
        """Verifies complete policy persistence, retrieval, and mapping correctness."""
        self.service.save_policy(self.policy)

        retrieved = self.service.get_policy(self.policy.policy_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.policy_id, self.policy.policy_id)
        self.assertEqual(retrieved.metadata.name, "Structural Layer Constraint")
        self.assertEqual(len(retrieved.rules), 1)
        self.assertEqual(retrieved.rules[0].name, "No ui to db")

    def test_get_policy_not_found(self) -> None:
        """Verifies get_policy returns None if not found."""
        self.assertIsNone(self.service.get_policy(uuid.uuid4()))

    def test_list_policies(self) -> None:
        """Verifies listing policies retrieves all items sorted deterministically by policy_id."""
        p1 = self.policy
        # Create a second policy
        meta2 = PolicyMetadata(
            name="Naming conventions",
            version="1.0.0",
            category="metric",
            created_at=self.time_utc,
        )
        p2 = GovernancePolicy(
            metadata=meta2,
            rules=(),
        )

        self.service.save_policy(p1)
        self.service.save_policy(p2)

        policies = self.service.list_policies()
        self.assertEqual(len(policies), 2)
        # Verify sorting is deterministic
        expected_ids = sorted([str(p1.policy_id), str(p2.policy_id)])
        self.assertEqual([str(p.policy_id) for p in policies], expected_ids)

    def test_update_policy(self) -> None:
        """Verifies policy updates apply atomically to existing policies."""
        self.service.save_policy(self.policy)

        # Create updated version
        updated_meta = PolicyMetadata(
            name="Structural Layer Constraint - V2",
            version="2.0.0",
            category="layer",
            created_at=self.time_utc,
        )
        updated_policy = GovernancePolicy(
            policy_id=self.policy.policy_id,
            metadata=updated_meta,
            rules=self.policy.rules,
        )

        self.service.update_policy(updated_policy)
        retrieved = self.service.get_policy(self.policy.policy_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.metadata.name, "Structural Layer Constraint - V2")
        self.assertEqual(retrieved.metadata.version, "2.0.0")

    def test_update_policy_not_found_raises(self) -> None:
        """Verifies updating a non-existent policy raises GovernanceValidationError."""
        with self.assertRaises(GovernanceValidationError):
            self.service.update_policy(self.policy)

    def test_save_and_retrieve_result(self) -> None:
        """Verifies GovernanceResult persistence and list operations scoped to project."""
        self.service.save_result(self.result)

        retrieved = self.service.get_result(self.result.result_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.result_id, self.result.result_id)
        self.assertEqual(retrieved.project_id, self.project_id)
        self.assertEqual(len(retrieved.violations), 1)

        # Retrieve list by project_id
        results_list = self.service.list_results(self.project_id)
        self.assertEqual(len(results_list), 1)
        self.assertEqual(results_list[0].result_id, self.result.result_id)

        # Retrieve list for different project
        empty_list = self.service.list_results(uuid.uuid4())
        self.assertEqual(len(empty_list), 0)

    def test_save_and_retrieve_violation_report(self) -> None:
        """Verifies Enriched violation reports persistence."""
        enriched = EnrichedViolation(
            rule_id=self.rule.rule_id,
            rule_name=self.rule.name,
            original_severity=ViolationSeverity.ERROR,
            refined_severity=ViolationSeverity.ERROR,
            priority_score=90.0,
            priority_tier="HIGH",
            root_cause="layer_boundary_bypass",
            impact_scope="layer_to_layer_link",
            suggested_remediation="Decouple.",
            original_message="UI refers to DB.",
            details={},
        )
        report = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            violations=(enriched,),
            violations_by_rule={self.rule.name: (enriched,)},
            violations_by_severity={ViolationSeverity.ERROR.value: 1},
        )

        self.service.save_violation_report(report)

        retrieved = self.service.get_violation_report(report.report_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.report_id, report.report_id)
        self.assertEqual(len(retrieved.violations), 1)
        self.assertEqual(retrieved.violations[0].priority_tier, "HIGH")

    def test_save_and_retrieve_compliance_report(self) -> None:
        """Verifies ComplianceReport persistence lifecycle."""
        comp_score = ComplianceScore(
            overall_score=85.0,
            category_scores={"layer": 85.0},
            repository_score=95.0,
            policy_coverage=0.0,
        )
        report = ComplianceReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            compliance_score=comp_score,
            violation_report_id=uuid.uuid4(),
        )

        self.service.save_compliance_report(report)

        retrieved = self.service.get_compliance_report(report.report_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.report_id, report.report_id)
        self.assertEqual(retrieved.compliance_score.overall_score, 85.0)

    def test_save_and_retrieve_analysis_result(self) -> None:
        """Verifies full GovernanceAnalysisResult DTO persistence."""
        comp_score = ComplianceScore(
            overall_score=85.0,
            category_scores={"layer": 85.0},
            repository_score=95.0,
            policy_coverage=0.0,
        )
        report_comp = ComplianceReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            compliance_score=comp_score,
            violation_report_id=uuid.uuid4(),
        )
        enriched = EnrichedViolation(
            rule_id=self.rule.rule_id,
            rule_name=self.rule.name,
            original_severity=ViolationSeverity.ERROR,
            refined_severity=ViolationSeverity.ERROR,
            priority_score=90.0,
            priority_tier="HIGH",
            root_cause="layer_boundary_bypass",
            impact_scope="layer_to_layer_link",
            suggested_remediation="Decouple.",
            original_message="UI refers to DB.",
            details={},
        )
        report_viol = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id=self.commit_id,
            generated_at=self.time_utc,
            violations=(enriched,),
            violations_by_rule={self.rule.name: (enriched,)},
            violations_by_severity={ViolationSeverity.ERROR.value: 1},
        )
        anal_res = GovernanceAnalysisResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            status=GovernanceStatus.FAILED,
            evaluation_result=self.result,
            violation_report=report_viol,
            compliance_report=report_comp,
            created_at=self.time_utc,
        )

        self.service.save_analysis_result(anal_res)

        retrieved = self.service.get_analysis_result(anal_res.result_id)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.result_id, anal_res.result_id)
        self.assertEqual(retrieved.status, GovernanceStatus.FAILED)
        self.assertEqual(retrieved.compliance_report.compliance_score.overall_score, 85.0)

    def test_serialization_and_deserialization_correctness(self) -> None:
        """Verifies repeated dumps preserve identical structure (serialization correctness)."""
        self.service.save_policy(self.policy)
        raw_data_1 = self.repo.get_policy(self.policy.policy_id)
        
        # Save again and retrieve
        self.service.save_policy(self.policy)
        raw_data_2 = self.repo.get_policy(self.policy.policy_id)

        self.assertEqual(raw_data_1, raw_data_2)

    def test_persistence_exception_translation(self) -> None:
        """Verifies physical database failures are cleanly translated to GovernancePersistenceError."""
        self.repo.toggle_failure(True)

        with self.assertRaises(GovernancePersistenceError):
            self.service.save_policy(self.policy)

        with self.assertRaises(GovernancePersistenceError):
            self.service.get_policy(self.policy.policy_id)

        with self.assertRaises(GovernancePersistenceError):
            self.service.list_policies()

        with self.assertRaises(GovernancePersistenceError):
            self.service.save_result(self.result)

        with self.assertRaises(GovernancePersistenceError):
            self.service.list_results(self.project_id)

    def test_deserialization_validation_failure(self) -> None:
        """Verifies Pydantic validations raise GovernanceValidationError if stored payload is corrupt."""
        self.service.save_policy(self.policy)

        # Corrupt data manually in database
        corrupt_data = self.repo.get_policy(self.policy.policy_id)
        corrupt_data["rules"] = [{"name": "invalid-rule-missing-fields"}]  # Invalid structure
        self.repo.save_policy(self.policy.policy_id, corrupt_data)

        with self.assertRaises(GovernanceValidationError):
            self.service.get_policy(self.policy.policy_id)

    def test_concurrent_persistence_scenarios(self) -> None:
        """Verifies concurrent executions do not cause race conditions or un-atomic writes."""
        num_threads = 10
        project_uuid = uuid.uuid4()
        
        def save_worker(idx: int) -> None:
            # Produce distinct result items
            res_item = GovernanceResult(
                result_id=uuid.uuid4(),
                project_id=project_uuid,
                commit_id=f"commit-{idx}",
                status=GovernanceStatus.PASSED,
                summary=GovernanceSummary(passed_count=idx, failed_count=0),
                created_at=self.time_utc,
            )
            self.service.save_result(res_item)

        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            futures = [executor.submit(save_worker, i) for i in range(num_threads)]
            for fut in futures:
                fut.result()

        # Retrieve list and verify all threads committed data safely
        results = self.service.list_results(project_uuid)
        self.assertEqual(len(results), num_threads)


if __name__ == "__main__":
    unittest.main()
