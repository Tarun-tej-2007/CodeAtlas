"""Integration tests for the Unified Analysis API endpoints."""

import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints.analyze import get_analysis_service
from app.parser.models import AnalysisResult
from app.schemas.analysis import AnalysisResponse, AnalysisStatus
from app.services.analysis import AnalysisService


class TestUnifiedAnalysisAPIIntegration(unittest.TestCase):
    """Verifies route dependencies, payload mapping, backward compatibility, and concurrent HTTP requests."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.mock_service = MagicMock(spec=AnalysisService)

        # Override dependency in app container
        app.dependency_overrides[get_analysis_service] = lambda: self.mock_service

        self.project_id = uuid.uuid4()
        self.repo_url = "https://github.com/test/repo"

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_default_backward_compatible_behavior(self) -> None:
        """Verifies default behavior is async accepted, returning no unified results (None)."""
        payload = {
            "repository_url": self.repo_url,
            "project_id": str(self.project_id),
        }
        response = self.client.post("/api/v1/analyze", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "accepted")
        self.assertIsNone(data["unified_result"])
        # Mock should not be invoked as default run is not sync
        self.mock_service.analyze_repository.assert_not_called()

    def test_synchronous_unified_analysis_route_injection(self) -> None:
        """Verifies endpoint triggers service correctly when run_sync parameter is requested."""
        mock_result = MagicMock(spec=AnalysisResult)
        mock_result.unified_result = {"project_health": "excellent"}
        self.mock_service.analyze_repository.return_value = mock_result

        payload = {
            "repository_url": self.repo_url,
            "project_id": str(self.project_id),
        }
        response = self.client.post("/api/v1/analyze?run_sync=true", json=payload)

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "completed")
        self.assertEqual(data["unified_result"], {"project_health": "excellent"})

        self.mock_service.analyze_repository.assert_called_once_with(
            repository_url=self.repo_url,
            project_id=self.project_id,
        )

    def test_exception_propagation(self) -> None:
        """Verifies exception raised by the service propagates through the API cleanly."""
        self.mock_service.analyze_repository.side_effect = RuntimeError("Pipeline error")

        payload = {
            "repository_url": self.repo_url,
            "project_id": str(self.project_id),
        }

        with self.assertRaises(RuntimeError) as ctx:
            self.client.post("/api/v1/analyze?run_sync=true", json=payload)
        self.assertEqual(str(ctx.exception), "Pipeline error")

    def test_deterministic_and_concurrent_http_calls(self) -> None:
        """Verifies deterministic mapping and thread safety over concurrent HTTP test calls."""
        mock_result = MagicMock(spec=AnalysisResult)
        mock_result.unified_result = {"project_health": "perfect"}
        self.mock_service.analyze_repository.return_value = mock_result

        payload = {
            "repository_url": self.repo_url,
            "project_id": str(self.project_id),
        }

        def post_request():
            return self.client.post("/api/v1/analyze?run_sync=true", json=payload)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(post_request) for _ in range(15)]
            responses = [f.result() for f in futures]

        for resp in responses:
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.json()["unified_result"], {"project_health": "perfect"})


if __name__ == "__main__":
    unittest.main()
