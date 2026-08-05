"""Integration tests for Technical Debt Analysis Integration."""

import unittest
import uuid
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock

from app.ai_service.enums import AIModelType, AIProvider, RequestPriority
from app.parser.models import AnalysisResult, ParseResult
from app.scanner.models import ScanResult, DiscoveryResult
from app.services.analysis import AnalysisService
from app.workspace.manager import WorkspaceManager, Workspace
from app.repositories.clone_service import RepositoryCloneService
from app.scanner.pipeline import ScannerPipeline
from app.parser.pipeline import ParsingPipeline
from app.semantic import SemanticPipeline, SemanticLinkingPipeline
from app.graph.dependency_builder import DependencyGraphBuilder
from app.technical_debt.engine import TechnicalDebtAnalysisEngine
from app.technical_debt.ai_analyzer import AITechnicalDebtAnalyzer


class TestTechnicalDebtAnalysisIntegration(unittest.TestCase):
    """Verifies end-to-end orchestration, optional execution, and backward compatibility."""

    def setUp(self) -> None:
        self.workspace_manager = MagicMock(spec=WorkspaceManager)
        self.clone_service = MagicMock(spec=RepositoryCloneService)
        self.scanner_pipeline = MagicMock(spec=ScannerPipeline)
        self.parsing_pipeline = MagicMock(spec=ParsingPipeline)
        self.semantic_pipeline = MagicMock(spec=SemanticPipeline)
        self.linking_pipeline = MagicMock(spec=SemanticLinkingPipeline)
        self.graph_builder = MagicMock(spec=DependencyGraphBuilder)

        # Baseline setups for mocks
        mock_workspace = MagicMock(spec=Workspace)
        mock_workspace.path = "temp_workspace"
        self.workspace_manager.create_workspace.return_value = mock_workspace

        self.mock_scan_res = MagicMock(spec=ScanResult)
        self.mock_scan_res.discovery_result = DiscoveryResult(files=[])
        self.scanner_pipeline.scan.return_value = self.mock_scan_res

        self.mock_parse_res = MagicMock(spec=ParseResult)
        self.mock_parse_res.files = []
        self.parsing_pipeline.parse_files.return_value = self.mock_parse_res

        # Tech debt mock analyzers
        self.mock_engine = MagicMock(spec=TechnicalDebtAnalysisEngine)
        self.mock_ai_analyzer = MagicMock(spec=AITechnicalDebtAnalyzer)
        self.mock_ai_analyzer.analysis_engine = self.mock_engine

    def test_backward_compatibility_no_tech_debt(self) -> None:
        """Verifies pipeline runs exactly as before if technical debt is not configured."""
        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            semantic_pipeline=self.semantic_pipeline,
            linking_pipeline=self.linking_pipeline,
            graph_builder=self.graph_builder,
            technical_debt_analyzer=None,
        )

        project_id = uuid.uuid4()
        result = service.analyze_repository(
            repository_url="https://github.com/test/repo",
            project_id=project_id,
        )

        self.assertIsInstance(result, AnalysisResult)
        self.assertIsNone(result.technical_debt_result)
        self.assertIsNone(result.architecture_result)

        # Verify no semantic/graph calls were made (since run_architecture and run_tech_debt are both False)
        self.semantic_pipeline.execute.assert_not_called()
        self.linking_pipeline.link_project.assert_not_called()

    def test_tech_debt_engine_only_execution(self) -> None:
        """Verifies rules scan runs when only the engine is injected (without AI)."""
        mock_report = MagicMock()
        self.mock_engine.analyze.return_value = mock_report

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            semantic_pipeline=self.semantic_pipeline,
            linking_pipeline=self.linking_pipeline,
            graph_builder=self.graph_builder,
            technical_debt_analyzer=self.mock_engine,
        )

        project_id = uuid.uuid4()
        result = service.analyze_repository(
            repository_url="https://github.com/test/repo",
            project_id=project_id,
        )

        self.assertIsInstance(result, AnalysisResult)
        self.assertEqual(result.technical_debt_result, mock_report)
        self.mock_engine.analyze.assert_called_once()
        self.mock_ai_analyzer.analyze.assert_not_called()

    def test_ai_technical_debt_analyzer_execution_with_ai(self) -> None:
        """Verifies AI analyzer runs when injected and AI provider/model are specified."""
        mock_ai_result = MagicMock()
        self.mock_ai_analyzer.analyze.return_value = mock_ai_result

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            semantic_pipeline=self.semantic_pipeline,
            linking_pipeline=self.linking_pipeline,
            graph_builder=self.graph_builder,
            technical_debt_analyzer=self.mock_ai_analyzer,
        )

        project_id = uuid.uuid4()
        result = service.analyze_repository(
            repository_url="https://github.com/test/repo",
            project_id=project_id,
            ai_provider=AIProvider.OPENAI,
            ai_model_type=AIModelType.BALANCED,
        )

        self.assertIsInstance(result, AnalysisResult)
        self.assertEqual(result.technical_debt_result, mock_ai_result)

        self.mock_ai_analyzer.analyze.assert_called_once()
        self.mock_engine.analyze.assert_not_called()

    def test_ai_technical_debt_analyzer_fallback_without_ai(self) -> None:
        """Verifies AI analyzer falls back to rule scan engine if AI options are missing."""
        mock_report = MagicMock()
        self.mock_engine.analyze.return_value = mock_report

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            semantic_pipeline=self.semantic_pipeline,
            linking_pipeline=self.linking_pipeline,
            graph_builder=self.graph_builder,
            technical_debt_analyzer=self.mock_ai_analyzer,
        )

        project_id = uuid.uuid4()
        result = service.analyze_repository(
            repository_url="https://github.com/test/repo",
            project_id=project_id,
        )

        self.assertIsInstance(result, AnalysisResult)
        self.assertEqual(result.technical_debt_result, mock_report)
        self.mock_engine.analyze.assert_called_once()
        self.mock_ai_analyzer.analyze.assert_not_called()

    def test_exception_propagation(self) -> None:
        """Verifies rule engine exceptions propagate cleanly during repository runs."""
        self.mock_engine.analyze.side_effect = RuntimeError("Scan engine crashed")

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            semantic_pipeline=self.semantic_pipeline,
            linking_pipeline=self.linking_pipeline,
            graph_builder=self.graph_builder,
            technical_debt_analyzer=self.mock_engine,
        )

        with self.assertRaises(RuntimeError) as ctx:
            service.analyze_repository(
                repository_url="https://github.com/test/repo",
                project_id=uuid.uuid4(),
            )
        self.assertEqual(str(ctx.exception), "Scan engine crashed")

    def test_deterministic_and_concurrent_execution(self) -> None:
        """Verifies integration execution outputs match deterministically and execute concurrently."""
        mock_report = MagicMock()
        self.mock_engine.analyze.return_value = mock_report

        service = AnalysisService(
            workspace_manager=self.workspace_manager,
            clone_service=self.clone_service,
            scanner_pipeline=self.scanner_pipeline,
            parsing_pipeline=self.parsing_pipeline,
            semantic_pipeline=self.semantic_pipeline,
            linking_pipeline=self.linking_pipeline,
            graph_builder=self.graph_builder,
            technical_debt_analyzer=self.mock_engine,
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
            self.assertEqual(res.technical_debt_result, mock_report)


if __name__ == "__main__":
    unittest.main()
