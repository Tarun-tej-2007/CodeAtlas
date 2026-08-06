"""Integration tests for the Architecture Evolution API endpoints."""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints.evolution import get_evolution_service, get_persistence_service
from app.evolution import (
    ArchitecturalRiskReport,
    ArchitectureSnapshot,
    ArchitectureEvolutionResult,
    ArchitectureEvolutionService,
    ArchitectureEvolutionPersistenceService,
    EvolutionMetadata,
    EvolutionRequest,
    EvolutionResult,
    EvolutionStatus,
    EvolutionSummary,
    EvolutionTrendResult,
)


class TestEvolutionAPIIntegration(unittest.TestCase):
    """Verifies authentication, payload validation, orchestrations, and query endpoints."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.auth_headers = {"Authorization": "Bearer supersecretjwtkey123!"}

        # Mock services
        self.mock_service = MagicMock(spec=ArchitectureEvolutionService)
        self.mock_persistence = MagicMock(spec=ArchitectureEvolutionPersistenceService)

        # Overrides
        app.dependency_overrides[get_evolution_service] = lambda: self.mock_service
        app.dependency_overrides[get_persistence_service] = lambda: self.mock_persistence

        self.client = TestClient(app)
        self.time_utc = datetime(2026, 8, 6, 12, 0, 0, tzinfo=timezone.utc)

        # DTO setups
        self.current_snap = ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id="c2",
            timestamp=self.time_utc,
            layers=(),
            components={},
        )
        self.prev_snap = ArchitectureSnapshot(
            snapshot_id=uuid.uuid4(),
            commit_id="c1",
            timestamp=self.time_utc,
            layers=(),
            components={},
        )
        self.summary = EvolutionSummary(added_count=0, removed_count=0, modified_count=0, unchanged_count=0)
        self.mock_trend = EvolutionTrendResult(
            coupling_trend=(0.1,),
            complexity_trend=(1.0,),
            tech_debt_trend=(5,),
            quality_trend=(90.0,),
            layer_stability=(1.0,),
            module_growth=(5,),
            summary={},
        )
        self.mock_risk_report = ArchitecturalRiskReport(
            report_id=uuid.uuid4(),
            generated_at=self.time_utc,
            overall_risk_score=0.0,
            risks=(),
        )

        self.evolution_result = ArchitectureEvolutionResult(
            evolution_result_id=uuid.uuid4(),
            request=EvolutionRequest(
                project_id=self.project_id,
                project_name="APIProj",
                source_commit="c1",
                target_commit="c2",
            ),
            current_snapshot=self.current_snap,
            previous_snapshot=self.prev_snap,
            changes=(),
            summary=self.summary,
            trends=self.mock_trend,
            risk_report=self.mock_risk_report,
        )

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_authentication_failures(self) -> None:
        """Verifies HTTP 401 response on missing or bad auth headers."""
        resp = self.client.post("/api/v1/evolution/analyze", json={})
        self.assertEqual(resp.status_code, 401)

    def test_authorization_failures(self) -> None:
        """Verifies HTTP 403 response on invalid Bearer tokens."""
        resp = self.client.post(
            "/api/v1/evolution/analyze",
            headers={"Authorization": "Bearer invalidtoken"},
            json={},
        )
        self.assertEqual(resp.status_code, 403)

    def test_validation_failures_bad_payload(self) -> None:
        """Verifies HTTP 422 response on missing payload parameters."""
        resp = self.client.post(
            "/api/v1/evolution/analyze",
            headers=self.auth_headers,
            json={"project_id": str(self.project_id)},  # Missing commits, name
        )
        self.assertEqual(resp.status_code, 422)

    def test_successful_evolution_analysis_request(self) -> None:
        """Verifies API starts and returns complete evolution DTO response."""
        self.mock_service.evolve_architecture.return_value = self.evolution_result

        payload = {
            "project_id": str(self.project_id),
            "project_name": "APIProj",
            "source_commit": "c1",
            "target_commit": "c2",
        }
        resp = self.client.post(
            "/api/v1/evolution/analyze",
            headers=self.auth_headers,
            json=payload,
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["request"]["project_name"], "APIProj")
        self.assertEqual(data["current_snapshot"]["commit_id"], "c2")

        # Verify persistence calls
        self.mock_persistence.save_snapshot.assert_called_once()
        self.mock_persistence.save_result.assert_called_once()
        self.mock_persistence.save_trend.assert_called_once()
        self.mock_persistence.save_risk_report.assert_called_once()

    def test_snapshot_retrieval(self) -> None:
        """Verifies snapshot endpoint retrieves serialized snapshots."""
        self.mock_persistence.get_snapshot.return_value = self.current_snap
        resp = self.client.get(
            "/api/v1/evolution/snapshot/c2",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["commit_id"], "c2")

    def test_snapshot_retrieval_not_found(self) -> None:
        """Verifies HTTP 404 response on missing snapshot hash."""
        self.mock_persistence.get_snapshot.return_value = None
        resp = self.client.get(
            "/api/v1/evolution/snapshot/c_missing",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 404)

    def test_result_retrieval(self) -> None:
        """Verifies result endpoint retrieves serialized EvolutionResult."""
        meta = EvolutionMetadata(
            project_name="APIProj",
            source_commit="c1",
            target_commit="c2",
            created_at=self.time_utc,
            status=EvolutionStatus.COMPLETED,
        )
        mock_res = EvolutionResult(
            evolution_id=uuid.uuid4(),
            metadata=meta,
            changes=(),
            summary=self.summary,
        )
        self.mock_persistence.get_result.return_value = mock_res

        rid = uuid.uuid4()
        resp = self.client.get(
            f"/api/v1/evolution/result/{rid}",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["metadata"]["project_name"], "APIProj")

    def test_trend_retrieval(self) -> None:
        """Verifies trend endpoint retrieves serialized EvolutionTrendResult."""
        self.mock_persistence.get_trend.return_value = self.mock_trend
        rid = uuid.uuid4()
        resp = self.client.get(
            f"/api/v1/evolution/trend/{rid}",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["coupling_trend"], [0.1])

    def test_risk_report_retrieval(self) -> None:
        """Verifies risk endpoint retrieves serialized ArchitecturalRiskReport."""
        self.mock_persistence.get_risk_report.return_value = self.mock_risk_report
        rid = uuid.uuid4()
        resp = self.client.get(
            f"/api/v1/evolution/risks/{rid}",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["overall_risk_score"], 0.0)


if __name__ == "__main__":
    unittest.main()
