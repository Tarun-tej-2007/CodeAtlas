"""Integration tests for the Architecture Governance API endpoints."""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints.governance import get_governance_service, get_persistence_service
from app.governance import (
    ComplianceReport,
    ComplianceScore,
    EnrichedViolation,
    GovernanceAnalysisResult,
    GovernancePolicy,
    GovernanceRequest,
    GovernanceResult,
    GovernanceViolationReport,
    PolicyMetadata,
    PolicyRule,
    PolicyViolation,
    ViolationSeverity,
    GovernanceStatus,
    GovernanceSummary,
)
from app.governance.service import GovernanceService
from app.governance.persistence import GovernancePersistenceService


class TestGovernanceAPIIntegration(unittest.TestCase):
    """Verifies authentication, payload validations, REST endpoints, and exception handling."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.auth_headers = {"Authorization": "Bearer supersecretjwtkey123!"}

        # Mock services
        self.mock_service = MagicMock(spec=GovernanceService)
        self.mock_persistence = MagicMock(spec=GovernancePersistenceService)

        # Overrides
        app.dependency_overrides[get_governance_service] = lambda: self.mock_service
        app.dependency_overrides[get_persistence_service] = lambda: self.mock_persistence

        self.client = TestClient(app)
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)

        # Fixtures
        self.policy_meta = PolicyMetadata(
            name="API Test Policy",
            version="1.0.0",
            category="layer",
            created_at=self.time_utc,
        )
        self.policy_rule = PolicyRule(
            name="No UI to DB import",
            rule_type="layer_ordering",
            severity=ViolationSeverity.ERROR,
            configuration={"allowed": ("utils",)},
        )
        self.policy = GovernancePolicy(
            metadata=self.policy_meta,
            rules=(self.policy_rule,),
        )
        self.violation = PolicyViolation(
            rule_id=self.policy_rule.rule_id,
            rule_name=self.policy_rule.name,
            severity=ViolationSeverity.ERROR,
            message="UI imports DB.",
        )
        self.eval_result = GovernanceResult(
            project_id=self.project_id,
            commit_id="commit-abc-123",
            status=GovernanceStatus.FAILED,
            violations=(self.violation,),
            summary=GovernanceSummary(passed_count=0, failed_count=1, warning_count=0, total_rules=1),
            created_at=self.time_utc,
        )
        self.enriched = EnrichedViolation(
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
        self.violation_report = GovernanceViolationReport(
            project_id=self.project_id,
            commit_id="commit-abc-123",
            generated_at=self.time_utc,
            violations=(self.enriched,),
            violations_by_rule={self.policy_rule.name: (self.enriched,)},
            violations_by_severity={ViolationSeverity.ERROR.value: 1},
        )
        self.comp_score = ComplianceScore(
            overall_score=85.0,
            category_scores={"layer": 85.0},
            repository_score=95.0,
            policy_coverage=0.0,
        )
        self.compliance_report = ComplianceReport(
            project_id=self.project_id,
            commit_id="commit-abc-123",
            generated_at=self.time_utc,
            compliance_score=self.comp_score,
            violation_report_id=self.violation_report.report_id,
        )
        self.analysis_result = GovernanceAnalysisResult(
            project_id=self.project_id,
            commit_id="commit-abc-123",
            status=GovernanceStatus.FAILED,
            evaluation_result=self.eval_result,
            violation_report=self.violation_report,
            compliance_report=self.compliance_report,
            created_at=self.time_utc,
        )

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_authentication_failures(self) -> None:
        """Verifies HTTP 401 response on missing or bad auth headers."""
        resp = self.client.post("/api/v1/governance/verify", json={})
        self.assertEqual(resp.status_code, 401)

        resp2 = self.client.post(
            "/api/v1/governance/verify",
            json={},
            headers={"Authorization": "Bearer badtoken"},
        )
        self.assertEqual(resp2.status_code, 403)

    def test_verify_governance_success(self) -> None:
        """Verifies successful verification orchestration flow."""
        self.mock_service.verify_governance.return_value = self.analysis_result

        request_payload = {
            "project_id": str(self.project_id),
            "project_name": "Atlas",
            "commit_id": "commit-abc-123",
            "policies": [self.policy.model_dump(mode="json")],
        }

        resp = self.client.post(
            "/api/v1/governance/verify",
            json=request_payload,
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "failed")
        self.assertEqual(data["project_id"], str(self.project_id))
        self.assertEqual(data["commit_id"], "commit-abc-123")

    def test_verify_governance_validation_failure(self) -> None:
        """Verifies payload validation errors trigger HTTP 422 Unprocessable Content."""
        request_payload = {
            "project_id": "not-a-uuid",  # invalid UUID triggers schema validation failure
            "project_name": "",
            "commit_id": "commit-abc-123",
            "policies": [],
        }

        resp = self.client.post(
            "/api/v1/governance/verify",
            json=request_payload,
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 422)

    def test_policy_crud_operations(self) -> None:
        """Verifies CRUD endpoints for GovernancePolicy models."""
        policy_id = self.policy.policy_id

        # 1. POST /policy
        self.mock_persistence.save_policy.return_value = None
        resp_post = self.client.post(
            "/api/v1/governance/policy",
            json=self.policy.model_dump(mode="json"),
            headers=self.auth_headers,
        )
        self.assertEqual(resp_post.status_code, 201)  # status.HTTP_201_CREATED
        self.assertEqual(resp_post.json()["status"], "created")
        self.assertEqual(resp_post.json()["policy_id"], str(policy_id))

        # 2. GET /policy/{policy_id}
        self.mock_persistence.get_policy.return_value = self.policy
        resp_get = self.client.get(
            f"/api/v1/governance/policy/{policy_id}",
            headers=self.auth_headers,
        )
        self.assertEqual(resp_get.status_code, 200)
        self.assertEqual(resp_get.json()["policy_id"], str(policy_id))

        # 3. PUT /policy
        self.mock_persistence.update_policy.return_value = None
        resp_put = self.client.put(
            "/api/v1/governance/policy",
            json=self.policy.model_dump(mode="json"),
            headers=self.auth_headers,
        )
        self.assertEqual(resp_put.status_code, 200)
        self.assertEqual(resp_put.json()["status"], "updated")

        # 4. GET /policies (List)
        self.mock_persistence.list_policies.return_value = (self.policy,)
        resp_list = self.client.get(
            "/api/v1/governance/policies",
            headers=self.auth_headers,
        )
        self.assertEqual(resp_list.status_code, 200)
        self.assertEqual(len(resp_list.json()), 1)
        self.assertEqual(resp_list.json()[0]["policy_id"], str(policy_id))

    def test_get_resource_not_found_handling(self) -> None:
        """Verifies HTTP 404 is returned when resources are missing."""
        missing_id = uuid.uuid4()
        
        # Policy missing
        self.mock_persistence.get_policy.return_value = None
        resp = self.client.get(f"/api/v1/governance/policy/{missing_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 404)

        # Result missing
        self.mock_persistence.get_result.return_value = None
        resp = self.client.get(f"/api/v1/governance/result/{missing_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 404)

        # Violation report missing
        self.mock_persistence.get_violation_report.return_value = None
        resp = self.client.get(f"/api/v1/governance/violation-report/{missing_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 404)

        # Compliance report missing
        self.mock_persistence.get_compliance_report.return_value = None
        resp = self.client.get(f"/api/v1/governance/compliance-report/{missing_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 404)

        # Analysis result missing
        self.mock_persistence.get_analysis_result.return_value = None
        resp = self.client.get(f"/api/v1/governance/analysis-result/{missing_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 404)

    def test_retrieve_run_data_endpoints(self) -> None:
        """Verifies retrieval endpoints for results, violations, compliance reports, and full analysis."""
        res_id = self.eval_result.result_id
        viol_id = self.violation_report.report_id
        comp_id = self.compliance_report.report_id
        anal_id = self.analysis_result.result_id

        # 1. GET /result/{result_id}
        self.mock_persistence.get_result.return_value = self.eval_result
        resp = self.client.get(f"/api/v1/governance/result/{res_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["result_id"], str(res_id))

        # 2. GET /results/{project_id}
        self.mock_persistence.list_results.return_value = (self.eval_result,)
        resp = self.client.get(f"/api/v1/governance/results/{self.project_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
        self.assertEqual(resp.json()[0]["result_id"], str(res_id))

        # 3. GET /violation-report/{report_id}
        self.mock_persistence.get_violation_report.return_value = self.violation_report
        resp = self.client.get(f"/api/v1/governance/violation-report/{viol_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["report_id"], str(viol_id))

        # 4. GET /compliance-report/{report_id}
        self.mock_persistence.get_compliance_report.return_value = self.compliance_report
        resp = self.client.get(f"/api/v1/governance/compliance-report/{comp_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["report_id"], str(comp_id))

        # 5. GET /analysis-result/{result_id}
        self.mock_persistence.get_analysis_result.return_value = self.analysis_result
        resp = self.client.get(f"/api/v1/governance/analysis-result/{anal_id}", headers=self.auth_headers)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["result_id"], str(anal_id))

    def test_deterministic_repeated_requests(self) -> None:
        """Verifies repeated identical GET requests retrieve matching payloads deterministically."""
        policy_id = self.policy.policy_id
        self.mock_persistence.get_policy.return_value = self.policy

        resp1 = self.client.get(f"/api/v1/governance/policy/{policy_id}", headers=self.auth_headers)
        resp2 = self.client.get(f"/api/v1/governance/policy/{policy_id}", headers=self.auth_headers)

        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp1.json(), resp2.json())


if __name__ == "__main__":
    unittest.main()
