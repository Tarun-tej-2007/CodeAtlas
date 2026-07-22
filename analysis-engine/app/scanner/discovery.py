"""File discovery service module.

Discovers repository files recursively while filtering ignored directories.
"""

import logging
from pathlib import Path

from app.scanner.exceptions import (
    DiscoveryFailureError,
    DiscoveryRootNotFoundError,
    InvalidDiscoveryRootError,
)
from app.scanner.models import DiscoveredFile, DiscoveryResult

logger = logging.getLogger("scanner")

DEFAULT_IGNORED_DIRECTORIES: set[str] = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
    "venv",
    ".env",
}


class FileDiscoveryService:
    """Recursively traverses directories to locate files, capturing metadata and ignoring config patterns."""

    def __init__(self, ignored_directories: set[str] | None = None) -> None:
        """Initializes FileDiscoveryService.

        Args:
            ignored_directories: Custom set of directories to ignore. Defaults to DEFAULT_IGNORED_DIRECTORIES.
        """
        self.ignored_directories = (
            ignored_directories if ignored_directories is not None else DEFAULT_IGNORED_DIRECTORIES
        )
        self.resolved_root: Path = Path()

    def discover_files(self, root_path: Path | str) -> DiscoveryResult:
        """Recursively traverses a root path, discovering all files not inside ignored directories.

        Args:
            root_path: Root filesystem path to traverse.

        Returns:
            A DiscoveryResult container model containing all discovered files.

        Raises:
            DiscoveryRootNotFoundError: If root_path does not exist.
            InvalidDiscoveryRootError: If root_path is not a directory.
            DiscoveryFailureError: If traversal fails due to filesystem errors.
        """
        try:
            self.resolved_root = Path(root_path).resolve()
        except Exception as err:
            raise InvalidDiscoveryRootError(f"Failed to resolve path '{root_path}': {err}") from err

        if not self.resolved_root.exists():
            raise DiscoveryRootNotFoundError(f"Discovery root path '{root_path}' does not exist.")

        if not self.resolved_root.is_dir():
            raise InvalidDiscoveryRootError(f"Discovery root path '{root_path}' is not a directory.")

        discovered_files = self._traverse(self.resolved_root)
        return DiscoveryResult(files=discovered_files)

    def _traverse(self, path: Path) -> list[DiscoveredFile]:
        """Recursive helper traversing directory children, bypassing ignored directories."""
        discovered: list[DiscoveredFile] = []
        try:
            for child in path.iterdir():
                if child.is_dir():
                    if child.name in self.ignored_directories:
                        continue
                    discovered.extend(self._traverse(child))
                elif child.is_file():
                    stat = child.stat()
                    # Calculate relative path safely
                    rel_path = child.relative_to(self.resolved_root)
                    discovered.append(
                        DiscoveredFile(
                            absolute_path=child.resolve(),
                            relative_path=rel_path,
                            extension=child.suffix,
                            size=stat.st_size,
                        )
                    )
        except PermissionError as err:
            logger.warning("Permission denied scanning directory '%s': %s", path, err)
        except Exception as err:
            raise DiscoveryFailureError(f"File discovery failed in directory '{path}': {err}") from err
        return discovered
