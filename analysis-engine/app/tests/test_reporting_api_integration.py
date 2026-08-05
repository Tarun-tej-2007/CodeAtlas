"""Integration tests for the Reporting API and Service endpoints."""

import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from app.main import app
from app.ai_service.enums import AIModelType, AIProvider
from app.api.v1.endpoints.analyze import get_analysis_service
from app.parser.models import AnalysisResult, ParseResult
from app.scanner.models import ScanResult, DiscoveryResult
from app.services.analysis import AnalysisService
from app.reporting.generator import ReportGenerator
from app.reporting.ai_analyzer import AIReportAnalyzer, AIReportAnalysisResult
from app.reporting.models import AnalysisReport, ReportMetadata
from app.reporting.enums import ReportFormat
from app.workspace.manager import WorkspaceManager, Workspace
from app.repositories.clone_service import RepositoryCloneService
from app.scanner.pipeline import ScannerPipeline
from app.parser.pipeline import ParsingPipeline


class TestReportingAPIIntegration(unittest.TestCase):
    """Verifies service orchestration fallback, DI overrides, API response fields, and concurrent runs."""

    def setUp(self) -> None:
        self.client = TestClient(app)
        self.project_id = uuid.uuid4()
        self.repo_url = "https://github.com/test/repo"

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

        # Reporting mocks
        self.mock_report_gen = MagicMock(spec=ReportGenerator)
        self.mock_ai_report_analyzer = MagicMock(spec=AIReportAnalyzer)

        # Precompiled mock report
        self.mock_compiled_report = MagicMock(spec=AnalysisReport)

    def test_reporting_disabled_by_default(self) -> None:
        """Verifies report_result is None when reporting services are not injected."""
        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            report_generator=None,
            ai_report_analyzer=None,
        )

        res = service.analyze_repository(self.repo_url, self.project_id)
        self.assertIsInstance(res, AnalysisResult)
        self.assertIsNone(res.report_result)

    def test_compilation_fallback_without_ai_config(self) -> None:
        """Verifies fallback returns AnalysisReport directly if AI options/analyzer are omitted."""
        self.mock_report_gen.generate.return_value = self.mock_compiled_report

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            report_generator=self.mock_report_gen,
            ai_report_analyzer=self.mock_ai_report_analyzer,
        )

        res = service.analyze_repository(self.repo_url, self.project_id)
        self.assertEqual(res.report_result, self.mock_compiled_report)
        self.mock_report_gen.generate.assert_called_once()
        self.mock_ai_report_analyzer.analyze.assert_not_called()

    def test_ai_orchestrated_compilation(self) -> None:
        """Verifies complete AI analysis is executed if generator and analyzer are configured with AI parameters."""
        self.mock_report_gen.generate.return_value = self.mock_compiled_report
        mock_ai_res = MagicMock(spec=AIReportAnalysisResult)
        self.mock_ai_report_analyzer.analyze.return_value = mock_ai_res

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            report_generator=self.mock_report_gen,
            ai_report_analyzer=self.mock_ai_report_analyzer,
        )

        res = service.analyze_repository(
            self.repo_url,
            self.project_id,
            ai_provider=AIProvider.OPENAI,
            ai_model_type=AIModelType.BALANCED,
        )

        self.assertEqual(res.report_result, mock_ai_res)
        self.mock_report_gen.generate.assert_called_once()
        self.mock_ai_report_analyzer.analyze.assert_called_once_with(
            report=self.mock_compiled_report,
            provider=AIProvider.OPENAI,
            model_type=AIModelType.BALANCED,
            variables=None,
            priority=unittest.mock.ANY,
            temperature=None,
            max_tokens=None,
        )

    def test_api_integration_sync_routes(self) -> None:
        """Verifies API endpoints return report results in responses when synchronous overrides occur."""
        # Setup mock service
        mock_analysis_service = MagicMock(spec=AnalysisService)
        mock_res = MagicMock(spec=AnalysisResult)
        mock_res.unified_result = None
        mock_res.report_result = {"project_name": "APIReport", "format": "json"}
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
            self.assertEqual(data["report_result"], {"project_name": "APIReport", "format": "json"})
        finally:
            app.dependency_overrides.clear()

    def test_exception_propagation(self) -> None:
        """Verifies reporting compilation exceptions propagate unmodified through the service wrapper."""
        self.mock_report_gen.generate.side_effect = RuntimeError("Compilation failed")

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            report_generator=self.mock_report_gen,
        )

        with self.assertRaises(RuntimeError) as ctx:
            service.analyze_repository(self.repo_url, self.project_id)
        self.assertEqual(str(ctx.exception), "Compilation failed")

    def test_concurrent_execution(self) -> None:
        """Verifies thread-safety during concurrent reporting pipeline calls."""
        self.mock_report_gen.generate.return_value = self.mock_compiled_report

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            report_generator=self.mock_report_gen,
        )

        def run_integration():
            return service.analyze_repository(self.repo_url, self.project_id)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_integration) for _ in range(15)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.report_result, self.mock_compiled_report)


if __name__ == "__main__":
    unittest.main()
