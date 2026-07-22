"""Analysis service module coordinating workspace, cloning, and scanning."""

import logging
import uuid

from app.workspace.manager import WorkspaceManager
from app.repositories.clone_service import RepositoryCloneService
from app.scanner.pipeline import ScannerPipeline
from app.scanner.models import ScanResult
from app.parser.pipeline import ParsingPipeline
from app.parser.models import AnalysisResult

logger = logging.getLogger("analysis-engine")


class AnalysisService:
    """Orchestrates codebase static analysis by preparing workspaces, acquiring code, scanning, and parsing."""

    def __init__(
        self,
        workspace_manager: WorkspaceManager | None = None,
        clone_service: RepositoryCloneService | None = None,
        scanner_pipeline: ScannerPipeline | None = None,
        parsing_pipeline: ParsingPipeline | None = None,
    ) -> None:
        """Initializes the AnalysisService with injected sub-services.

        Args:
            workspace_manager: Optional WorkspaceManager override.
            clone_service: Optional RepositoryCloneService override.
            scanner_pipeline: Optional ScannerPipeline override.
            parsing_pipeline: Optional ParsingPipeline override.
        """
        self.workspace_manager = workspace_manager or WorkspaceManager()
        self.clone_service = clone_service or RepositoryCloneService()
        self.scanner_pipeline = scanner_pipeline or ScannerPipeline()
        self.parsing_pipeline = parsing_pipeline or ParsingPipeline()

    def analyze_repository(self, repository_url: str, project_id: uuid.UUID) -> AnalysisResult:
        """Runs the static analysis and parsing pipeline on the given repository URL.

        1. Creates an isolated workspace.
        2. Clones or copies the repository files.
        3. Scans the workspace to discover files and identify languages.
        4. Parses discovered files.
        5. Guarantees workspace cleanup (if configured to delete).

        Args:
            repository_url: Local path or remote Git URL.
            project_id: Project identifier to isolate the workspace.

        Returns:
            The aggregated AnalysisResult containing scan and parse outputs.
        """
        workspace = self.workspace_manager.create_workspace(analysis_id=project_id)
        
        try:
            self.clone_service.clone_repository(source=repository_url, workspace=workspace)
            scan_result = self.scanner_pipeline.scan(repository_root=workspace.path)
            
            # Execute parsing pipeline
            discovered_files = scan_result.discovery_result.files
            parse_result = self.parsing_pipeline.parse_files(discovered_files)
            
            return AnalysisResult(scan_result=scan_result, parse_result=parse_result)
        finally:
            try:
                self.workspace_manager.cleanup_workspace(workspace)
            except Exception as cleanup_err:
                logger.error(
                    "Failed to clean up workspace at '%s' after analysis: %s",
                    workspace.path,
                    cleanup_err,
                    exc_info=True,
                )
                # We log the cleanup failure but do not raise it,
                # ensuring the original exception (if any) or result propagates untouched.

