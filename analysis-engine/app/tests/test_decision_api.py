"""Integration tests for the Architecture Decision Intelligence API endpoints."""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints.decision import get_decision_service, get_persistence_service
from app.decision import (
    ArchitectureDecision,
    DecisionCategory,
    DecisionPriority,
    DecisionStatus,
    DecisionMetadata,
    DecisionRequest,
    DecisionTraceGraph,
    DecisionDriftReport,
    DecisionHealthReport,
    DecisionHealth,
    DecisionAnalysisResult,
    DecisionIntelligenceService,
    DecisionPersistenceService,
    DecisionValidationError,
)


class TestDecisionAPIIntegration(unittest.TestCase):
    """Verifies authentication, HTTP status translations, and CRUD retrieval endpoints."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.decision_id = uuid.uuid4()
        self.auth_headers = {"Authorization": "Bearer supersecretjwtkey123!"}

        # Mock Services
        self.mock_service = MagicMock(spec=DecisionIntelligenceService)
        self.mock_persistence = MagicMock(spec=DecisionPersistenceService)
        self.mock_repository = MagicMock()
        self.mock_persistence.repository = self.mock_repository

        # Dependency Overrides
        app.dependency_overrides[get_decision_service] = lambda: self.mock_service
        app.dependency_overrides[get_persistence_service] = lambda: self.mock_persistence

        self.client = TestClient(app)
        self.time_utc = datetime(2026, 8, 7, 12, 0, 0, tzinfo=timezone.utc)

        # Fixtures
        self.decision = ArchitectureDecision(
            decision_id=self.decision_id,
            title="Use FastAPI",
            category=DecisionCategory.DESIGN,
            status=DecisionStatus.ACCEPTED,
            priority=DecisionPriority.CRITICAL,
            context="Legacy framework is slow.",
            decision_text="We choose FastAPI.",
            consequences="Fast API development.",
            metadata=DecisionMetadata(
                author="Lead Architect",
                created_at=self.time_utc,
                updated_at=self.time_utc,
                extra_info={"targets": ("file:src/app.py",)},
            ),
        )

        self.trace_graph = DecisionTraceGraph(
            project_id=self.project_id,
            commit_id="commit-abc-123",
            links=(),
        )

        self.drift_report = DecisionDriftReport(
            project_id=self.project_id,
            commit_id="commit-abc-123",
            drifts=(),
        )

        self.health_report = DecisionHealthReport(
            project_id=self.project_id,
            commit_id="commit-abc-123",
            health=DecisionHealth(
                overall_score=100.0,
                classification="Excellent",
                recommendations=(),
            ),
        )

        self.analysis_result = DecisionAnalysisResult(
            project_id=self.project_id,
            commit_id="commit-abc-123",
            decisions=(self.decision,),
            trace_graph=self.trace_graph,
            drift_report=self.drift_report,
            health_report=self.health_report,
            processed_at=self.time_utc,
        )

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_unauthorized_request(self) -> None:
        """Verifies endpoints reject requests with missing or invalid token headers."""
        response = self.client.post("/api/v1/decision/analyze", json={})
        self.assertEqual(response.status_code, 401)

    def test_successful_analysis_execution(self) -> None:
        """Verifies POST /api/v1/decision/analyze handles valid payloads and returns results."""
        self.mock_service.analyze_project_decisions.return_value = self.analysis_result

        payload = {
            "project_id": str(self.project_id),
            "commit_id": "commit-abc-123",
            "requests": [
                {
                    "project_id": str(self.project_id),
                    "decision": {
                        "decision_id": str(self.decision_id),
                        "title": "Use FastAPI",
                        "category": "design",
                        "status": "accepted",
                        "priority": "critical",
                        "context": "Legacy framework is slow.",
                        "decision_text": "We choose FastAPI.",
                        "consequences": "Fast API development.",
                        "metadata": {
                            "author": "Lead Architect",
                            "created_at": self.time_utc.isoformat(),
                            "updated_at": self.time_utc.isoformat(),
                            "extra_info": {"targets": ["file:src/app.py"]},
                        },
                    },
                }
            ],
        }

        response = self.client.post(
            "/api/v1/decision/analyze",
            json=payload,
            headers=self.auth_headers,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["project_id"], str(self.project_id))
        self.assertEqual(len(response.json()["decisions"]), 1)

    def test_invalid_payload_validation_fails(self) -> None:
        """Verifies endpoint returns HTTP 422 Bad Request on missing fields."""
        payload = {
            "project_id": str(self.project_id),
            # Missing commit_id
        }
        response = self.client.post(
            "/api/v1/decision/analyze",
            json=payload,
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 422)

    def test_get_decision_success(self) -> None:
        """Verifies GET /api/v1/decision/{decision_id} returns decision payload."""
        self.mock_persistence.get_decision.return_value = self.decision

        response = self.client.get(
            f"/api/v1/decision/{self.decision_id}",
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["decision_id"], str(self.decision_id))

    def test_get_decision_not_found(self) -> None:
        """Verifies GET /api/v1/decision/{decision_id} returns HTTP 404 on missing record."""
        self.mock_persistence.get_decision.return_value = None

        response = self.client.get(
            f"/api/v1/decision/{uuid.uuid4()}",
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 404)

    def test_get_trace_graph_success(self) -> None:
        """Verifies GET /api/v1/decision/trace/{decision_id} resolves context and returns trace graph."""
        self.mock_persistence.get_decision.return_value = self.decision
        self.mock_repository.list_keys_starting_with.side_effect = [
            [f"decision:{self.project_id}:{self.decision_id}"],
            [f"trace:{self.project_id}:commit-abc-123"],
        ]
        self.mock_persistence.get_trace_graph.return_value = self.trace_graph

        response = self.client.get(
            f"/api/v1/decision/trace/{self.decision_id}",
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["project_id"], str(self.project_id))


if __name__ == "__main__":
    unittest.main()
