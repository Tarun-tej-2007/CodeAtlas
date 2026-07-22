"""Analysis service module coordinating workspace, cloning, and scanning."""

import logging
import uuid

from app.workspace.manager import WorkspaceManager
from app.repositories.clone_service import RepositoryCloneService
from app.scanner.pipeline import ScannerPipeline
from app.scanner.models import ScanResult

logger = logging.getLogger("analysis-engine")


class AnalysisService:
    """Orchestrates codebase static analysis by preparing workspaces, acquiring code, and scanning."""

    def __init__(
        self,
        workspace_manager: WorkspaceManager | None = None,
        clone_service: RepositoryCloneService | None = None,
        scanner_pipeline: ScannerPipeline | None = None,
    ) -> None:
        """Initializes the AnalysisService with injected sub-services.

        Args:
            workspace_manager: Optional WorkspaceManager override.
            clone_service: Optional RepositoryCloneService override.
            scanner_pipeline: Optional ScannerPipeline override.
        """
        self.workspace_manager = workspace_manager or WorkspaceManager()
        self.clone_service = clone_service or RepositoryCloneService()
        self.scanner_pipeline = scanner_pipeline or ScannerPipeline()

    def analyze_repository(self, repository_url: str, project_id: uuid.UUID) -> ScanResult:
        """Runs the static analysis pipeline on the given repository URL.

        1. Creates an isolated workspace.
        2. Clones or copies the repository files.
        3. Scans the workspace to discover files and identify languages.
        4. Guarantees workspace cleanup (if configured to delete).

        Args:
            repository_url: Local path or remote Git URL.
            project_id: Project identifier to isolate the workspace.

        Returns:
            The ScanResult.
        """
        workspace = self.workspace_manager.create_workspace(analysis_id=project_id)
        
        try:
            self.clone_service.clone_repository(source=repository_url, workspace=workspace)
            scan_result = self.scanner_pipeline.scan(repository_root=workspace.path)
            return scan_result
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
