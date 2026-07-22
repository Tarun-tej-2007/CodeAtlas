"""Unit tests for the AnalysisService orchestrator."""

import unittest
import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

from app.workspace import Workspace, WorkspaceManager
from app.workspace.exceptions import WorkspaceCreationError
from app.repositories import RepositoryCloneService, RepositoryCloneError
from app.scanner import ScannerPipeline, ScanResult, DiscoveryResult
from app.parser import ParsingPipeline, ParseResult, AnalysisResult
from app.services import AnalysisService


class TestAnalysisService(unittest.TestCase):
    """Tests the orchestration flow inside AnalysisService."""

    def setUp(self) -> None:
        self.project_id = uuid.uuid4()
        self.repo_url = "https://github.com/user/project.git"

        # Mock dependencies
        self.mock_workspace_manager = MagicMock(spec=WorkspaceManager)
        self.mock_clone_service = MagicMock(spec=RepositoryCloneService)
        self.mock_scanner_pipeline = MagicMock(spec=ScannerPipeline)
        self.mock_parsing_pipeline = MagicMock(spec=ParsingPipeline)

        self.service = AnalysisService(
            workspace_manager=self.mock_workspace_manager,
            clone_service=self.mock_clone_service,
            scanner_pipeline=self.mock_scanner_pipeline,
            parsing_pipeline=self.mock_parsing_pipeline,
        )

        # Mocked outputs
        self.mock_workspace = Workspace(
            id=uuid.uuid4(),
            analysis_id=self.project_id,
            path=Path("/tmp/codeatlas/analysis-1"),
            created_at=MagicMock(),
        )
        self.mock_scan_result = MagicMock(spec=ScanResult)
        self.mock_scan_result.discovery_result = DiscoveryResult(files=[])
        self.mock_parse_result = MagicMock(spec=ParseResult)

    def test_successful_orchestration_flow(self) -> None:
        # Arrange
        self.mock_workspace_manager.create_workspace.return_value = self.mock_workspace
        self.mock_scanner_pipeline.scan.return_value = self.mock_scan_result
        self.mock_parsing_pipeline.parse_files.return_value = self.mock_parse_result

        # Act
        result = self.service.analyze_repository(self.repo_url, self.project_id)

        # Assert
        self.assertIsInstance(result, AnalysisResult)
        self.assertEqual(result.scan_result, self.mock_scan_result)
        self.assertEqual(result.parse_result, self.mock_parse_result)

        # Verify orchestration sequence
        self.mock_workspace_manager.create_workspace.assert_called_once_with(analysis_id=self.project_id)
        self.mock_clone_service.clone_repository.assert_called_once_with(
            source=self.repo_url, workspace=self.mock_workspace
        )
        self.mock_scanner_pipeline.scan.assert_called_once_with(
            repository_root=self.mock_workspace.path
        )
        self.mock_parsing_pipeline.parse_files.assert_called_once_with([])
        # 2. Workspace cleanup after success
        self.mock_workspace_manager.cleanup_workspace.assert_called_once_with(self.mock_workspace)

    def test_workspace_cleanup_on_repository_acquisition_failure(self) -> None:
        # Arrange
        self.mock_workspace_manager.create_workspace.return_value = self.mock_workspace
        self.mock_clone_service.clone_repository.side_effect = RepositoryCloneError("Clone failed")

        # 4. Repository acquisition failure propagation & 3. Workspace cleanup after failure
        with self.assertRaises(RepositoryCloneError):
            self.service.analyze_repository(self.repo_url, self.project_id)

        # Assert cleanup occurred
        self.mock_workspace_manager.cleanup_workspace.assert_called_once_with(self.mock_workspace)
        self.mock_scanner_pipeline.scan.assert_not_called()

    def test_workspace_cleanup_on_scanner_pipeline_failure(self) -> None:
        # Arrange
        self.mock_workspace_manager.create_workspace.return_value = self.mock_workspace
        self.mock_scanner_pipeline.scan.side_effect = RuntimeError("Scanner crashed")

        # 5. Scanner pipeline failure propagation & 7. Cleanup execution on exceptions
        with self.assertRaises(RuntimeError):
            self.service.analyze_repository(self.repo_url, self.project_id)

        # Assert cleanup occurred
        self.mock_workspace_manager.cleanup_workspace.assert_called_once_with(self.mock_workspace)

    def test_dependency_injection_behavior(self) -> None:
        # 6. Dependency injection
        custom_service = AnalysisService()
        self.assertIsInstance(custom_service.workspace_manager, WorkspaceManager)
        self.assertIsInstance(custom_service.clone_service, RepositoryCloneService)
        self.assertIsInstance(custom_service.scanner_pipeline, ScannerPipeline)
        self.assertIsInstance(custom_service.parsing_pipeline, ParsingPipeline)

    def test_cleanup_failure_does_not_suppress_original_exception(self) -> None:
        # Arrange
        self.mock_workspace_manager.create_workspace.return_value = self.mock_workspace
        self.mock_scanner_pipeline.scan.side_effect = RuntimeError("Original error")
        self.mock_workspace_manager.cleanup_workspace.side_effect = Exception("Cleanup failed")

        # Original error should bubble up, cleanup error is logged but not raised
        with self.assertRaises(RuntimeError) as ctx:
            self.service.analyze_repository(self.repo_url, self.project_id)

        self.assertEqual(str(ctx.exception), "Original error")
        self.mock_workspace_manager.cleanup_workspace.assert_called_once()


if __name__ == "__main__":
    unittest.main()

