"""Integration tests for the Dashboard API and Service endpoints."""

import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.api.v1.endpoints.analyze import get_analysis_service
from app.parser.models import AnalysisResult, ParseResult
from app.scanner.models import ScanResult, DiscoveryResult
from app.services.analysis import AnalysisService
from app.dashboard import DashboardModel, DashboardMetadata, DashboardStatus
from app.dashboard.engine import DashboardAggregationEngine
from app.workspace.manager import WorkspaceManager, Workspace
from app.repositories.clone_service import RepositoryCloneService
from app.scanner.pipeline import ScannerPipeline
from app.parser.pipeline import ParsingPipeline


class TestDashboardAPIIntegration(unittest.TestCase):
    """Verifies service orchestration fallback, DI overrides, API response mapping, and concurrency."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.project_id = uuid.uuid4()
        self.repo_url = "https://github.com/dashboard/repo"

        # Mock Pipeline items
        self.workspace_manager = MagicMock(spec=WorkspaceManager)
        self.clone_service = MagicMock(spec=RepositoryCloneService)
        self.scanner_pipeline = MagicMock(spec=ScannerPipeline)
        self.parsing_pipeline = MagicMock(spec=ParsingPipeline)

        mock_workspace = MagicMock(spec=Workspace)
        mock_workspace.path = "temp_workspace"
        self.workspace_manager.create_workspace.return_value = mock_workspace

        self.mock_scan_res = MagicMock(spec=ScanResult)
        self.mock_scan_res.discovery_result = DiscoveryResult(files=[])
        self.scanner_pipeline.scan.return_value = self.mock_scan_res

        self.mock_parse_res = MagicMock(spec=ParseResult)
        self.mock_parse_res.files = []
        self.parsing_pipeline.parse_files.return_value = self.mock_parse_res

        # Dashboard mocks
        self.mock_dashboard_engine = MagicMock(spec=DashboardAggregationEngine)
        self.mock_dashboard_model = MagicMock(spec=DashboardModel)

    def test_dashboard_disabled_by_default(self) -> None:
        """Verifies dashboard_result is None when dashboard_engine is not injected."""
        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            dashboard_engine=None,
        )

        res = service.analyze_repository(self.repo_url, self.project_id)
        self.assertIsInstance(res, AnalysisResult)
        self.assertIsNone(res.dashboard_result)

    def test_dashboard_enabled(self) -> None:
        """Verifies dashboard aggregation compiles and maps output when dashboard_engine is supplied."""
        self.mock_dashboard_engine.compile.return_value = self.mock_dashboard_model

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            dashboard_engine=self.mock_dashboard_engine,
        )

        res = service.analyze_repository(self.repo_url, self.project_id)
        self.assertEqual(res.dashboard_result, self.mock_dashboard_model)
        self.mock_dashboard_engine.compile.assert_called_once()

    def test_api_integration_sync_routes(self) -> None:
        """Verifies API endpoints return dashboard results in responses when synchronous overrides occur."""
        # Setup mock service
        mock_analysis_service = MagicMock(spec=AnalysisService)
        mock_res = MagicMock(spec=AnalysisResult)
        mock_res.unified_result = None
        mock_res.report_result = None
        mock_res.dashboard_result = {"project_name": "APIDashboard", "status": "ready"}
        mock_analysis_service.analyze_repository.return_value = mock_res

        # Dependency override
        app.dependency_overrides[get_analysis_service] = lambda: mock_analysis_service

        try:
            payload = {
                "repository_url": self.repo_url,
                "project_id": str(self.project_id),
            }
            response = self.client.post("/api/v1/analyze?run_sync=true", json=payload)

            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "completed")
            self.assertEqual(data["dashboard_result"], {"project_name": "APIDashboard", "status": "ready"})
        finally:
            app.dependency_overrides.clear()

    def test_exception_propagation(self) -> None:
        """Verifies aggregation exceptions propagate unmodified through the service wrapper."""
        self.mock_dashboard_engine.compile.side_effect = RuntimeError("Aggregation failure")

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            dashboard_engine=self.mock_dashboard_engine,
        )

        with self.assertRaises(RuntimeError) as ctx:
            service.analyze_repository(self.repo_url, self.project_id)
        self.assertEqual(str(ctx.exception), "Aggregation failure")

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety during parallel, concurrent service sweeps."""
        self.mock_dashboard_engine.compile.return_value = self.mock_dashboard_model

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            dashboard_engine=self.mock_dashboard_engine,
        )

        def run_integration():
            return service.analyze_repository(self.repo_url, self.project_id)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_integration) for _ in range(15)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.dashboard_result, self.mock_dashboard_model)


if __name__ == "__main__":
    unittest.main()
