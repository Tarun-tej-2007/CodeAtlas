"""End-to-end tests for the complete Dashboard workflow, AI, and Persistence."""

import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from app.ai_service.enums import AIModelType, AIProvider
from app.parser.models import AnalysisResult, ParseResult
from app.scanner.models import ScanResult, DiscoveryResult
from app.services.analysis import AnalysisService
from app.dashboard import DashboardModel, DashboardMetadata, DashboardStatus
from app.dashboard.engine import DashboardAggregationEngine
from app.dashboard.ai_analyzer import AIDashboardAnalyzer, AIDashboardAnalysisResult
from app.dashboard.persistence import DashboardPersistenceService
from app.workspace.manager import WorkspaceManager, Workspace
from app.repositories.clone_service import RepositoryCloneService
from app.scanner.pipeline import ScannerPipeline
from app.parser.pipeline import ParsingPipeline


class TestDashboardEndToEnd(unittest.TestCase):
    """Verifies workflow orchestration permutations, persistence saves, failure propagation, and thread safety."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.repo_url = "https://github.com/e2e-dashboard/repo"

        # Mock Pipeline items
        self.workspace_manager = MagicMock(spec=WorkspaceManager)
        self.clone_service = MagicMock(spec=RepositoryCloneService)
        self.scanner_pipeline = MagicMock(spec=ScannerPipeline)
        self.parsing_pipeline = MagicMock(spec=ParsingPipeline)

        mock_workspace = MagicMock(spec=Workspace)
        mock_workspace.path = "e2e_dashboard_workspace"
        self.workspace_manager.create_workspace.return_value = mock_workspace

        self.mock_scan_res = MagicMock(spec=ScanResult)
        self.mock_scan_res.discovery_result = DiscoveryResult(files=[])
        self.scanner_pipeline.scan.return_value = self.mock_scan_res

        self.mock_parse_res = MagicMock(spec=ParseResult)
        self.mock_parse_res.files = []
        self.parsing_pipeline.parse_files.return_value = self.mock_parse_res

        # Dashboard & Persistence mocks
        self.mock_dashboard_engine = MagicMock(spec=DashboardAggregationEngine)
        self.mock_ai_dashboard_analyzer = MagicMock(spec=AIDashboardAnalyzer)
        self.mock_persistence_service = MagicMock(spec=DashboardPersistenceService)

        # Precompiled mock dashboard
        self.mock_compiled_dashboard = MagicMock(spec=DashboardModel)
        self.mock_dashboard_engine.compile.return_value = self.mock_compiled_dashboard

    def test_dashboard_only(self) -> None:
        """Verifies dashboard compilation runs but bypasses AI and persistence when not provided."""
        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            dashboard_engine=self.mock_dashboard_engine,
            ai_dashboard_analyzer=None,
            dashboard_persistence_service=None,
        )

        res = service.analyze_repository(self.repo_url, self.project_id)
        self.assertEqual(res.dashboard_result, self.mock_compiled_dashboard)
        self.mock_dashboard_engine.compile.assert_called_once()
        self.mock_ai_dashboard_analyzer.analyze.assert_not_called()
        self.mock_persistence_service.save_dashboard.assert_not_called()

    def test_dashboard_plus_ai(self) -> None:
        """Verifies dashboard generation triggers AI analyzer but bypasses persistence when persistence is not provided."""
        mock_ai_res = MagicMock(spec=AIDashboardAnalysisResult)
        self.mock_ai_dashboard_analyzer.analyze.return_value = mock_ai_res

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            dashboard_engine=self.mock_dashboard_engine,
            ai_dashboard_analyzer=self.mock_ai_dashboard_analyzer,
            dashboard_persistence_service=None,
        )

        res = service.analyze_repository(
            self.repo_url,
            self.project_id,
            ai_provider=AIProvider.OPENAI,
            ai_model_type=AIModelType.BALANCED,
        )
        self.assertEqual(res.dashboard_result, mock_ai_res)
        self.mock_ai_dashboard_analyzer.analyze.assert_called_once()
        self.mock_persistence_service.save_dashboard.assert_not_called()

    def test_dashboard_plus_persistence(self) -> None:
        """Verifies dashboard generation triggers persistence but bypasses AI analyzer when AI parameters are omitted."""
        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            dashboard_engine=self.mock_dashboard_engine,
            ai_dashboard_analyzer=None,
            dashboard_persistence_service=self.mock_persistence_service,
        )

        res = service.analyze_repository(self.repo_url, self.project_id)
        self.assertEqual(res.dashboard_result, self.mock_compiled_dashboard)
        self.mock_persistence_service.save_dashboard.assert_called_once_with(self.mock_compiled_dashboard)
        self.mock_ai_dashboard_analyzer.analyze.assert_not_called()

    def test_dashboard_plus_ai_plus_persistence(self) -> None:
        """Verifies dashboard generation triggers both AI analysis and persists the AI result output."""
        mock_ai_res = MagicMock(spec=AIDashboardAnalysisResult)
        self.mock_ai_dashboard_analyzer.analyze.return_value = mock_ai_res

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            dashboard_engine=self.mock_dashboard_engine,
            ai_dashboard_analyzer=self.mock_ai_dashboard_analyzer,
            dashboard_persistence_service=self.mock_persistence_service,
        )

        res = service.analyze_repository(
            self.repo_url,
            self.project_id,
            ai_provider=AIProvider.OPENAI,
            ai_model_type=AIModelType.BALANCED,
        )
        self.assertEqual(res.dashboard_result, mock_ai_res)
        self.mock_ai_dashboard_analyzer.analyze.assert_called_once()
        self.mock_persistence_service.save_dashboard.assert_called_once_with(mock_ai_res)

    def test_persistence_failures(self) -> None:
        """Verifies persistence service failures propagate directly up the invocation stack."""
        self.mock_persistence_service.save_dashboard.side_effect = RuntimeError("DB write error")

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            dashboard_engine=self.mock_dashboard_engine,
            dashboard_persistence_service=self.mock_persistence_service,
        )

        with self.assertRaises(RuntimeError) as ctx:
            service.analyze_repository(self.repo_url, self.project_id)
        self.assertEqual(str(ctx.exception), "DB write error")

    def test_concurrent_execution(self) -> None:
        """Verifies thread safety under concurrent, multi-threaded pipelines orchestration."""
        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            dashboard_engine=self.mock_dashboard_engine,
            dashboard_persistence_service=self.mock_persistence_service,
        )

        def run_e2e():
            return service.analyze_repository(self.repo_url, self.project_id)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_e2e) for _ in range(15)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.dashboard_result, self.mock_compiled_dashboard)


if __name__ == "__main__":
    unittest.main()
