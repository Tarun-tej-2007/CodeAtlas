"""Integration tests for the Incremental Analysis API and endpoints."""

import unittest
import uuid
from unittest.mock import MagicMock
from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints.incremental import get_incremental_service, get_persistence_service
from app.graph.dependency_graph import DependencyGraph
from app.incremental import (
    ChangeType,
    ChangedFile,
    IncrementalAnalysisMetadata,
    IncrementalAnalysisResult,
    IncrementalAnalysisService,
    IncrementalStatus,
    RepositorySnapshot,
    IncrementalAnalysisPersistenceService,
    FileFingerprint,
)


class TestIncrementalAPIIntegration(unittest.TestCase):
    """Verifies authentication guards, API DTO request validations, orchestrations, and sorting correctness."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.repo_root = "c:/Users/tarun/OneDrive/Desktop/projects/CodeAtlas/analysis-engine/app/tests/temp_dir"
        self.auth_headers = {"Authorization": "Bearer supersecretjwtkey123!"}

        # Mock services
        self.mock_service = MagicMock(spec=IncrementalAnalysisService)
        self.mock_persistence = MagicMock(spec=IncrementalAnalysisPersistenceService)

        # Overrides
        app.dependency_overrides[get_incremental_service] = lambda: self.mock_service
        app.dependency_overrides[get_persistence_service] = lambda: self.mock_persistence

        self.client = TestClient(app)

        from datetime import datetime, timezone
        self.time_utc = datetime.now(timezone.utc)
        self.analysis_id = uuid.uuid4()
        metadata = IncrementalAnalysisMetadata(
            project_name="APIProj",
            source_commit="c1",
            target_commit="c2",
            created_at=self.time_utc,
            status=IncrementalStatus.COMPLETED,
        )
        self.mock_result = IncrementalAnalysisResult(
            analysis_id=self.analysis_id,
            metadata=metadata,
            added_count=1,
            modified_count=0,
            deleted_count=0,
            unchanged_count=0,
            changed_files=(
                ChangedFile(path="src/a.py", change_type=ChangeType.ADDED),
            ),
        )

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_authentication_failures(self) -> None:
        """Verifies HTTP 401 response when Authorization header is omitted."""
        resp = self.client.post("/api/v1/incremental/analyze", json={})
        self.assertEqual(resp.status_code, 401)
        self.assertIn("Missing Authorization header", resp.json()["detail"])

        # Invalid scheme
        resp = self.client.post(
            "/api/v1/incremental/analyze",
            headers={"Authorization": "Basic admin:password"},
            json={},
        )
        self.assertEqual(resp.status_code, 401)

    def test_authorization_failures(self) -> None:
        """Verifies HTTP 403 response when token is invalid."""
        resp = self.client.post(
            "/api/v1/incremental/analyze",
            headers={"Authorization": "Bearer badtoken"},
            json={},
        )
        self.assertEqual(resp.status_code, 403)
        self.assertIn("Forbidden", resp.json()["detail"])

    def test_successful_incremental_analysis_request(self) -> None:
        """Verifies HTTP 200 and DTO fields mapping on successful analysis submission."""
        self.mock_service.analyze_incrementally.return_value = self.mock_result

        payload = {
            "project_id": str(self.project_id),
            "project_name": "APIProj",
            "repository_root": self.repo_root,
            "source_commit": "c1",
            "target_commit": "c2",
            "nodes": [{"id": "src/a.py", "name": "a.py", "type": "module"}],
            "edges": [],
        }

        resp = self.client.post(
            "/api/v1/incremental/analyze",
            headers=self.auth_headers,
            json=payload,
        )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["analysis_id"], str(self.analysis_id))
        self.assertEqual(data["added_count"], 1)

        # Check call arguments
        args, kwargs = self.mock_service.analyze_incrementally.call_args
        self.assertEqual(kwargs["project_id"], self.project_id)
        self.assertEqual(kwargs["project_name"], "APIProj")
        self.assertIsInstance(kwargs["dependency_graph"], DependencyGraph)

    def test_validation_failures_on_empty_fields(self) -> None:
        """Verifies FastAPI request schema validation rejects empty strings or missing fields."""
        payload = {
            "project_id": str(self.project_id),
            "project_name": "",  # Empty name
            "repository_root": self.repo_root,
            "source_commit": "c1",
            "target_commit": "c2",
        }

        resp = self.client.post(
            "/api/v1/incremental/analyze",
            headers=self.auth_headers,
            json=payload,
        )
        self.assertEqual(resp.status_code, 422)

    def test_get_snapshot_success_and_missing(self) -> None:
        """Verifies HTTP 200 for snapshot retrieval and 404 for missing commits."""
        # Success mock
        snap = RepositorySnapshot(commit_id="c2", fingerprints={})
        self.mock_persistence.get_snapshot.return_value = snap

        resp = self.client.get(
            "/api/v1/incremental/snapshot/c2",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["commit_id"], "c2")

        # Missing mock
        self.mock_persistence.get_snapshot.return_value = None
        resp = self.client.get(
            "/api/v1/incremental/snapshot/missing_commit",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 404)

    def test_get_result_success_and_missing(self) -> None:
        """Verifies HTTP 200 for metadata result retrieval and 404 if missing."""
        # Success mock
        self.mock_persistence.get_result.return_value = self.mock_result

        resp = self.client.get(
            f"/api/v1/incremental/result/{self.analysis_id}",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["analysis_id"], str(self.analysis_id))

        # Missing mock
        self.mock_persistence.get_result.return_value = None
        resp = self.client.get(
            f"/api/v1/incremental/result/{uuid.uuid4()}",
            headers=self.auth_headers,
        )
        self.assertEqual(resp.status_code, 404)

    def test_get_changes_deterministic_ordering(self) -> None:
        """Verifies file changes retrieval enforces deterministic alphabetical path ordering."""
        # Result containing unsorted file changes
        res_with_unsorted = IncrementalAnalysisResult(
            analysis_id=self.analysis_id,
            metadata=self.mock_result.metadata,
            added_count=3,
            modified_count=0,
            deleted_count=0,
            unchanged_count=0,
            changed_files=(
                ChangedFile(path="src/z.py", change_type=ChangeType.ADDED),
                ChangedFile(path="src/a.py", change_type=ChangeType.ADDED),
                ChangedFile(path="src/m.py", change_type=ChangeType.ADDED),
            ),
        )
        self.mock_persistence.get_result.return_value = res_with_unsorted

        resp = self.client.get(
            f"/api/v1/incremental/changes/{self.analysis_id}",
            headers=self.auth_headers,
        )

        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 3)
        # Verify alphabetical sorting (a, m, z)
        self.assertEqual(data[0]["path"], "src/a.py")
        self.assertEqual(data[1]["path"], "src/m.py")
        self.assertEqual(data[2]["path"], "src/z.py")


if __name__ == "__main__":
    unittest.main()
