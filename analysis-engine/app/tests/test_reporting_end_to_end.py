"""End-to-end tests for the complete Reporting workflow and Persistence."""

import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from app.ai_service.enums import AIModelType, AIProvider
from app.parser.models import AnalysisResult, ParseResult
from app.scanner.models import ScanResult, DiscoveryResult
from app.services.analysis import AnalysisService
from app.reporting.generator import ReportGenerator
from app.reporting.ai_analyzer import AIReportAnalyzer, AIReportAnalysisResult
from app.reporting.persistence import ReportPersistenceService
from app.reporting.models import AnalysisReport, ReportMetadata
from app.reporting.enums import ReportFormat
from app.workspace.manager import WorkspaceManager, Workspace
from app.repositories.clone_service import RepositoryCloneService
from app.scanner.pipeline import ScannerPipeline
from app.parser.pipeline import ParsingPipeline


class TestReportingEndToEnd(unittest.TestCase):
    """Verifies workflow orchestration permutations, persistence saves, failure propagation, and thread safety."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.repo_url = "https://github.com/e2e/repo"

        # Mock Pipeline items
        self.workspace_manager = MagicMock(spec=WorkspaceManager)
        self.clone_service = MagicMock(spec=RepositoryCloneService)
        self.scanner_pipeline = MagicMock(spec=ScannerPipeline)
        self.parsing_pipeline = MagicMock(spec=ParsingPipeline)

        mock_workspace = MagicMock(spec=Workspace)
        mock_workspace.path = "e2e_workspace"
        self.workspace_manager.create_workspace.return_value = mock_workspace

        self.mock_scan_res = MagicMock(spec=ScanResult)
        self.mock_scan_res.discovery_result = DiscoveryResult(files=[])
        self.scanner_pipeline.scan.return_value = self.mock_scan_res

        self.mock_parse_res = MagicMock(spec=ParseResult)
        self.mock_parse_res.files = []
        self.parsing_pipeline.parse_files.return_value = self.mock_parse_res

        # Reporting & Persistence mocks
        self.mock_report_gen = MagicMock(spec=ReportGenerator)
        self.mock_ai_report_analyzer = MagicMock(spec=AIReportAnalyzer)
        self.mock_persistence_service = MagicMock(spec=ReportPersistenceService)

        # Precompiled mock report
        self.mock_compiled_report = MagicMock(spec=AnalysisReport)
        self.mock_report_gen.generate.return_value = self.mock_compiled_report

    def test_reporting_only(self) -> None:
        """Verifies report generation compiles but bypasses AI and persistence when not provided."""
        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            report_generator=self.mock_report_gen,
            ai_report_analyzer=None,
            report_persistence_service=None,
        )

        res = service.analyze_repository(self.repo_url, self.project_id)
        self.assertEqual(res.report_result, self.mock_compiled_report)
        self.mock_report_gen.generate.assert_called_once()
        self.mock_ai_report_analyzer.analyze.assert_not_called()
        self.mock_persistence_service.save_report.assert_not_called()

    def test_reporting_plus_ai(self) -> None:
        """Verifies report generation triggers AI analyzer but bypasses persistence when persistence is not provided."""
        mock_ai_res = MagicMock(spec=AIReportAnalysisResult)
        self.mock_ai_report_analyzer.analyze.return_value = mock_ai_res

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            report_generator=self.mock_report_gen,
            ai_report_analyzer=self.mock_ai_report_analyzer,
            report_persistence_service=None,
        )

        res = service.analyze_repository(
            self.repo_url,
            self.project_id,
            ai_provider=AIProvider.OPENAI,
            ai_model_type=AIModelType.BALANCED,
        )
        self.assertEqual(res.report_result, mock_ai_res)
        self.mock_ai_report_analyzer.analyze.assert_called_once()
        self.mock_persistence_service.save_report.assert_not_called()

    def test_reporting_plus_persistence(self) -> None:
        """Verifies report generation triggers persistence but bypasses AI analyzer when AI parameters are omitted."""
        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            report_generator=self.mock_report_gen,
            ai_report_analyzer=None,
            report_persistence_service=self.mock_persistence_service,
        )

        res = service.analyze_repository(self.repo_url, self.project_id)
        self.assertEqual(res.report_result, self.mock_compiled_report)
        self.mock_persistence_service.save_report.assert_called_once_with(self.mock_compiled_report)
        self.mock_ai_report_analyzer.analyze.assert_not_called()

    def test_reporting_plus_ai_plus_persistence(self) -> None:
        """Verifies report generation triggers both AI analysis and persists the AI result output."""
        mock_ai_res = MagicMock(spec=AIReportAnalysisResult)
        self.mock_ai_report_analyzer.analyze.return_value = mock_ai_res

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            report_generator=self.mock_report_gen,
            ai_report_analyzer=self.mock_ai_report_analyzer,
            report_persistence_service=self.mock_persistence_service,
        )

        res = service.analyze_repository(
            self.repo_url,
            self.project_id,
            ai_provider=AIProvider.OPENAI,
            ai_model_type=AIModelType.BALANCED,
        )
        self.assertEqual(res.report_result, mock_ai_res)
        self.mock_ai_report_analyzer.analyze.assert_called_once()
        self.mock_persistence_service.save_report.assert_called_once_with(mock_ai_res)

    def test_persistence_failures(self) -> None:
        """Verifies persistence service failures propagate directly up the invocation stack."""
        self.mock_persistence_service.save_report.side_effect = RuntimeError("DB write error")

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            report_generator=self.mock_report_gen,
            report_persistence_service=self.mock_persistence_service,
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
            report_generator=self.mock_report_gen,
            report_persistence_service=self.mock_persistence_service,
        )

        def run_e2e():
            return service.analyze_repository(self.repo_url, self.project_id)

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_e2e) for _ in range(15)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.report_result, self.mock_compiled_report)


if __name__ == "__main__":
    unittest.main()
