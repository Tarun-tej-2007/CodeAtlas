"""Integration tests for Unified Analysis Integration."""

import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from app.parser.models import AnalysisResult, ParseResult
from app.scanner.models import ScanResult, DiscoveryResult
from app.services.analysis import AnalysisService
from app.workspace.manager import WorkspaceManager, Workspace
from app.repositories.clone_service import RepositoryCloneService
from app.scanner.pipeline import ScannerPipeline
from app.parser.pipeline import ParsingPipeline
from app.unified_analysis.engine import UnifiedAnalysisEngine


class TestUnifiedAnalysisIntegration(unittest.TestCase):
    """Verifies orchestration injection, reuse of outputs, context aggregation, and backward compatibility."""

    def setUp(self) -> None:
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

        self.mock_unified_analyzer = MagicMock(spec=UnifiedAnalysisEngine)

    def test_backward_compatibility_no_unified_analyzer(self) -> None:
        """Verifies unified analysis skips if analyzer is omitted."""
        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            unified_analysis_analyzer=None,
        )

        result = service.analyze_repository(
            repository_url="https://github.com/test/repo",
            project_id=uuid.uuid4(),
        )

        self.assertIsInstance(result, AnalysisResult)
        self.assertIsNone(result.unified_result)
        self.mock_unified_analyzer.analyze.assert_not_called()

    def test_unified_aggregation_execution_and_context(self) -> None:
        """Verifies engine is invoked, receives compiled context, and attaches report."""
        mock_report = MagicMock()
        self.mock_unified_analyzer.analyze.return_value = mock_report

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            unified_analysis_analyzer=self.mock_unified_analyzer,
        )

        result = service.analyze_repository(
            repository_url="https://github.com/test/repo",
            project_id=uuid.uuid4(),
        )

        self.assertIsInstance(result, AnalysisResult)
        self.assertEqual(result.unified_result, mock_report)

        # Verify analyze was called and context properties mapped correctly
        self.mock_unified_analyzer.analyze.assert_called_once()
        call_kwargs = self.mock_unified_analyzer.analyze.call_args[1]
        context = call_kwargs["context"]

        self.assertEqual(context.scan_result, self.mock_scan_res)
        self.assertEqual(context.parse_result, self.mock_parse_res)
        self.assertIsNone(context.architecture_result)
        self.assertIsNone(context.technical_debt_result)

    def test_exception_propagation(self) -> None:
        """Verifies exception propagates cleanly without wrapping."""
        self.mock_unified_analyzer.analyze.side_effect = RuntimeError("Unified engine fail")

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            unified_analysis_analyzer=self.mock_unified_analyzer,
        )

        with self.assertRaises(RuntimeError) as ctx:
            service.analyze_repository(
                repository_url="https://github.com/test/repo",
                project_id=uuid.uuid4(),
            )
        self.assertEqual(str(ctx.exception), "Unified engine fail")

    def test_deterministic_and_concurrent_execution(self) -> None:
        """Verifies deterministic return values and thread safety during concurrent pipeline runs."""
        mock_report = MagicMock()
        self.mock_unified_analyzer.analyze.return_value = mock_report

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            unified_analysis_analyzer=self.mock_unified_analyzer,
        )

        def run_integration():
            return service.analyze_repository(
                repository_url="https://github.com/test/repo",
                project_id=uuid.uuid4(),
            )

        with ThreadPoolExecutor(max_workers=8) as executor:
            futures = [executor.submit(run_integration) for _ in range(15)]
            results = [f.result() for f in futures]

        for res in results:
            self.assertEqual(res.unified_result, mock_report)


if __name__ == "__main__":
    unittest.main()
