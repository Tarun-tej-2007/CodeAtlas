"""Integration tests for the AI Architecture Intelligence API endpoints."""

import unittest
import uuid
from datetime import datetime, timezone
from unittest.mock import MagicMock

from fastapi import status
from fastapi.testclient import TestClient

from app.api.v1.endpoints.ai import get_ai_orchestrator, get_persistence_service
from app.ai import (
    AIAnalysis,
    AIAnalysisStatus,
    AIAnalysisType,
    AIOrchestratorService,
    AIProviderError,
    AIRecommendation,
    AIResult,
    AIUsageStatistics,
    AIValidationError,
    AIPersistenceError,
    AIAnalysisPersistenceService,
    ArchitectureReview,
    RefactoringRoadmap,
)
from app.main import app


class TestAIAPIIntegration(unittest.TestCase):
    """Verifies security token checks, request mapping, error handling, and GET endpoints."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.analysis_id = uuid.uuid4()
        self.commit_id = "commit-123-abc"
        self.auth_headers = {"Authorization": "Bearer supersecretjwtkey123!"}

        # Mock Services
        self.mock_orchestrator = MagicMock(spec=AIOrchestratorService)
        self.mock_persistence = MagicMock(spec=AIAnalysisPersistenceService)

        # Dependency Overrides
        app.dependency_overrides[get_ai_orchestrator] = lambda: self.mock_orchestrator
        app.dependency_overrides[get_persistence_service] = lambda: self.mock_persistence

        self.client = TestClient(app)
        self.time_utc = datetime(2026, 8, 7, 10, 0, 0, tzinfo=timezone.utc)

        # Fixtures
        self.analysis = AIAnalysis(
            analysis_id=self.analysis_id,
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis_type=AIAnalysisType.FULL_ARCHITECTURE_REVIEW,
            status=AIAnalysisStatus.COMPLETED,
            started_at=self.time_utc,
            completed_at=self.time_utc,
            statistics=AIUsageStatistics(prompt_tokens=100, completion_tokens=50, total_tokens=150),
            recommendations=(
                AIRecommendation(
                    title="Fix Layer violation",
                    description="Decouple API from direct DB query.",
                    category="architecture",
                    priority="critical",
                ),
            ),
        )
        self.review = ArchitectureReview(
            project_id=self.project_id,
            commit_id=self.commit_id,
            executive_summary="Review Executive Summary text",
            roadmap=RefactoringRoadmap(estimated_workload="low"),
        )
        self.result = AIResult(
            project_id=self.project_id,
            commit_id=self.commit_id,
            analysis=self.analysis,
            extra_info={"review": self.review},
        )

    def tearDown(self) -> None:
        # Clear dependency overrides to prevent interference with other API tests
        app.dependency_overrides.clear()

    def test_unauthorized_request(self) -> None:
        """Verifies access is blocked without Bearer JWT token."""
        response = self.client.post("/api/v1/ai/analyze", json={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Test forbidden (invalid token)
        response = self.client.post(
            "/api/v1/ai/analyze",
            json={},
            headers={"Authorization": "Bearer badtoken"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_successful_analysis_request(self) -> None:
        """Verifies successful POST /analyze triggers orchestrator and yields serialized DTO."""
        self.mock_orchestrator.orchestrate_analysis.return_value = self.result

        payload = {
            "project_id": str(self.project_id),
            "commit_id": self.commit_id,
            "analysis_type": "full_architecture_review",
            "custom_instructions": "Guidelines text",
        }
        response = self.client.post(
            "/api/v1/ai/analyze",
            json=payload,
            headers=self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.json()
        self.assertEqual(data["project_id"], str(self.project_id))
        self.assertEqual(data["commit_id"], self.commit_id)
        self.assertEqual(data["analysis"]["status"], "completed")

    def test_validation_failure_translates_to_400(self) -> None:
        """Verifies AIValidationError translates to HTTP 400."""
        self.mock_orchestrator.orchestrate_analysis.side_effect = AIValidationError("Bad inputs")

        payload = {
            "project_id": str(self.project_id),
            "commit_id": self.commit_id,
            "analysis_type": "full_architecture_review",
        }
        response = self.client.post(
            "/api/v1/ai/analyze",
            json=payload,
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Bad inputs", response.json()["detail"])

    def test_provider_failure_translates_to_502(self) -> None:
        """Verifies AIProviderError translates to HTTP 502 Bad Gateway."""
        self.mock_orchestrator.orchestrate_analysis.side_effect = AIProviderError("LLM failed")

        payload = {
            "project_id": str(self.project_id),
            "commit_id": self.commit_id,
            "analysis_type": "full_architecture_review",
        }
        response = self.client.post(
            "/api/v1/ai/analyze",
            json=payload,
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_502_BAD_GATEWAY)
        self.assertIn("LLM failed", response.json()["detail"])

    def test_persistence_failure_translates_to_500(self) -> None:
        """Verifies AIPersistenceError translates to HTTP 500."""
        self.mock_orchestrator.orchestrate_analysis.side_effect = AIPersistenceError("DB write timeout")

        payload = {
            "project_id": str(self.project_id),
            "commit_id": self.commit_id,
            "analysis_type": "full_architecture_review",
        }
        response = self.client.post(
            "/api/v1/ai/analyze",
            json=payload,
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    def test_successful_get_analysis_record(self) -> None:
        """Verifies retrieval endpoint /analysis/{analysis_id} returning the stored run DTO."""
        self.mock_persistence.get_analysis.return_value = self.analysis

        response = self.client.get(
            f"/api/v1/ai/analysis/{self.analysis_id}",
            headers=self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["analysis_id"], str(self.analysis_id))
        self.assertEqual(data["status"], "completed")

    def test_get_analysis_missing_returns_404(self) -> None:
        """Verifies missing records yield HTTP 404."""
        self.mock_persistence.get_analysis.return_value = None

        response = self.client.get(
            f"/api/v1/ai/analysis/{uuid.uuid4()}",
            headers=self.auth_headers,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_review_endpoint(self) -> None:
        """Verifies compiled review retrieval endpoint /review/{analysis_id}."""
        self.mock_persistence.get_analysis.return_value = self.analysis
        self.mock_persistence.get_result.return_value = self.result

        response = self.client.get(
            f"/api/v1/ai/review/{self.analysis_id}",
            headers=self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["executive_summary"], "Review Executive Summary text")

    def test_get_recommendations_endpoint(self) -> None:
        """Verifies recommendations retrieval endpoint /recommendations/{analysis_id}."""
        self.mock_persistence.get_analysis.return_value = self.analysis

        response = self.client.get(
            f"/api/v1/ai/recommendations/{self.analysis_id}",
            headers=self.auth_headers,
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Fix Layer violation")


if __name__ == "__main__":
    unittest.main()
