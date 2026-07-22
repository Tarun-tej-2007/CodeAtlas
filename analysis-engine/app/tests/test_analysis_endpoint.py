"""Unit tests for the Analysis Engine '/api/v1/analyze' endpoint."""

import unittest
import uuid
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app
from app.schemas.analysis import AnalysisStatus


class TestAnalysisEndpoint(unittest.TestCase):
    """Tests for the Analysis Engine direct HTTP controller."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.project_id = uuid.uuid4()

    def test_submit_analysis_endpoint_success(self) -> None:
        payload = {
            "repository_url": "https://github.com/user/project-repo",
            "project_id": str(self.project_id),
        }
        response = self.client.post(
            "/api/v1/analyze",
            json=payload,
            headers={"X-Request-ID": "custom-req-id"}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        
        self.assertIn("job_id", data)
        # Should be a valid UUID
        uuid.UUID(data["job_id"])
        
        self.assertEqual(data["status"], AnalysisStatus.ACCEPTED.value)
        self.assertEqual(data["project_id"], str(self.project_id))
        self.assertEqual(data["repository_url"], "https://github.com/user/project-repo")
        self.assertIn("received", data["message"].lower())
        
        # Verify request correlation ID in headers
        self.assertEqual(response.headers.get("X-Request-ID"), "custom-req-id")

    def test_submit_analysis_endpoint_missing_fields(self) -> None:
        payload = {
            "repository_url": "https://github.com/user/project-repo",
        }
        response = self.client.post("/api/v1/analyze", json=payload)
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_version_endpoint_analysis_engine(self) -> None:
        response = self.client.get("/api/v1/version")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data["service"], "CodeAtlas Analysis Engine")
        self.assertEqual(data["version"], "0.10.5")
        self.assertEqual(data["build"], "development")
