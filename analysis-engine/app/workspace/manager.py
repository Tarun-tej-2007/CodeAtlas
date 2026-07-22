"""Workspace manager module."""

from datetime import datetime, timezone
import logging
from pathlib import Path
import shutil
import uuid

from app.core.config import settings
from app.workspace.exceptions import (
    WorkspaceAlreadyExistsError,
    WorkspaceCleanupError,
    WorkspaceCreationError,
    WorkspaceNotFoundError,
)
from app.workspace.models import Workspace

logger = logging.getLogger("workspace")


class WorkspaceManager:
    """Manages temporary filesystem analysis directories."""

    def __init__(self, workspace_root: Path = None, keep_workspace: bool = None) -> None:
        """Initializes WorkspaceManager with config overrides.

        Args:
            workspace_root: Optional filesystem root path override.
            keep_workspace: Optional skip-deletion flag override.
        """
        self.workspace_root = workspace_root or settings.WORKSPACE_ROOT
        self.keep_workspace = keep_workspace if keep_workspace is not None else settings.KEEP_WORKSPACE

    def get_workspace_path(self, analysis_id: uuid.UUID) -> Path:
        """Resolves the absolute path for an analysis workspace directory.

        Args:
            analysis_id: Unique analysis ID.

        Returns:
            Resolved filesystem Path.
        """
        return self.workspace_root / str(analysis_id)

    def create_workspace(self, analysis_id: uuid.UUID) -> Workspace:
        """Creates an isolated directory for the specific analysis job.

        Args:
            analysis_id: Unique analysis ID.

        Returns:
            A Workspace instance.

        Raises:
            WorkspaceAlreadyExistsError: If the directory exists.
            WorkspaceCreationError: If creation fails.
        """
        try:
            # 1. Resolve and create workspace root if necessary
            self.workspace_root.mkdir(parents=True, exist_ok=True)
        except Exception as err:
            raise WorkspaceCreationError(f"Failed to create workspace root directory '{self.workspace_root}': {err}") from err

        path = self.get_workspace_path(analysis_id)
        if path.exists():
            raise WorkspaceAlreadyExistsError(f"Workspace directory '{path}' already exists.")

        try:
            path.mkdir(parents=True)
        except Exception as err:
            raise WorkspaceCreationError(f"Failed to create isolated workspace directory '{path}': {err}") from err

        return Workspace(
            id=uuid.uuid4(),
            analysis_id=analysis_id,
            path=path,
            created_at=datetime.now(timezone.utc),
        )

    def cleanup_workspace(self, workspace: Workspace) -> None:
        """Recursively removes a workspace directory.

        Args:
            workspace: The Workspace to clean up.

        Raises:
            WorkspaceNotFoundError: If directory does not exist.
            WorkspaceCleanupError: If deletion fails.
        """
        if self.keep_workspace:
            logger.info("Skipping workspace cleanup for '%s' due to KEEP_WORKSPACE config.", workspace.path)
            return

        if not workspace.path.exists():
            raise WorkspaceNotFoundError(f"Cannot clean up workspace '{workspace.path}': directory not found.")

        try:
            shutil.rmtree(workspace.path)
        except Exception as err:
            raise WorkspaceCleanupError(f"Failed to recursively clean up workspace directory '{workspace.path}': {err}") from err

    def workspace_exists(self, workspace: Workspace) -> bool:
        """Checks if a workspace directory exists on the filesystem.

        Args:
            workspace: The Workspace instance.

        Returns:
            True if it exists, False otherwise.
        """
        return workspace.path.exists()
