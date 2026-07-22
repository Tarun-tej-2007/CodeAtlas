"""Repository clone service module."""

import logging
from pathlib import Path
import shutil
import subprocess
from typing import Any

from app.repositories.exceptions import (
    InvalidRepositorySourceError,
    RepositoryCloneError,
    RepositoryCopyError,
    RepositoryNotFoundError,
)

logger = logging.getLogger("repositories")


class RepositoryCloneService:
    """Service responsible for acquiring repository source files into a workspace."""

    def clone_repository(self, source: str, workspace: Any) -> Path:
        """Acquires a repository from local disk or Git URL into the workspace.

        Args:
            source: Local filesystem directory path or Git clone URL.
            workspace: The target Workspace object.

        Returns:
            The Path inside the workspace where files are acquired.

        Raises:
            InvalidRepositorySourceError: If the source is empty or malformed.
            RepositoryNotFoundError: If a local source directory does not exist.
            RepositoryCopyError: If copying a local directory fails.
            RepositoryCloneError: If the git clone process execution fails.
        """
        if not source or not isinstance(source, str):
            raise InvalidRepositorySourceError("Repository source must be a non-empty string.")

        if not workspace or not hasattr(workspace, "path") or not isinstance(workspace.path, Path):
            raise InvalidRepositorySourceError("Workspace must be a valid Workspace instance with a pathlib.Path path.")

        dest_path = workspace.path
        source_path = Path(source)

        is_git = self._is_git_url(source)

        if not is_git:
            # If not classified as git URL, treat it as a local path
            if not source_path.exists():
                raise RepositoryNotFoundError(f"Local repository source '{source}' does not exist.")
            if not source_path.is_dir():
                raise InvalidRepositorySourceError(f"Local source '{source}' is not a directory.")

            try:
                logger.info("Copying local directory from '%s' to '%s'", source_path, dest_path)
                shutil.copytree(source_path, dest_path, dirs_exist_ok=True)
                return dest_path
            except Exception as err:
                raise RepositoryCopyError(f"Failed to copy local directory '{source_path}' to '{dest_path}': {err}") from err

        # Otherwise run Git clone
        try:
            logger.info("Cloning Git repository from '%s' to '%s'", source, dest_path)
            subprocess.run(
                ["git", "clone", source, str(dest_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            return dest_path
        except subprocess.CalledProcessError as err:
            stderr_msg = err.stderr.strip() if err.stderr else str(err)
            raise RepositoryCloneError(f"Git clone failed: {stderr_msg}") from err
        except Exception as err:
            raise RepositoryCloneError(f"Unexpected error executing Git clone: {err}") from err

    def _is_git_url(self, source: str) -> bool:
        """Helper to classify if source matches standard Git URL patterns."""
        src_lower = source.lower()
        return (
            src_lower.startswith("http://")
            or src_lower.startswith("https://")
            or src_lower.startswith("git@")
            or src_lower.endswith(".git")
        )
