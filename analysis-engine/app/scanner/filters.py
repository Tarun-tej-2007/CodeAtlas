"""Scan filtering and exclusion module.

Provides the FilteringEngine class responsible for evaluating whether files
or directories should be traversed, processed, or skipped based on configuration options.
"""

from pathlib import Path

from app.scanner.config import ScannerConfig
from app.scanner.constants import (
    IGNORED_DIRECTORIES,
    IGNORED_FILES,
    SUPPORTED_EXTENSIONS,
)


class FilteringEngine:
    """Evaluates whether directories and files should be processed or excluded."""

    def __init__(
        self,
        config: ScannerConfig | None = None,
        ignored_directories: set[str] | frozenset[str] | None = None,
        ignored_files: set[str] | frozenset[str] | None = None,
        supported_extensions: set[str] | frozenset[str] | None = None,
    ) -> None:
        """Initializes the filtering engine with configuration options and filter sets.

        Args:
            config: Optional ScannerConfig instance controlling filtering behavior.
            ignored_directories: Optional custom set of directory names to ignore.
            ignored_files: Optional custom set of filenames to ignore.
            supported_extensions: Optional custom set of supported file extensions.
        """
        self.config = config or ScannerConfig()

        if ignored_directories is not None:
            self.ignored_directories: frozenset[str] = frozenset(ignored_directories)
        elif self.config.respect_default_filters:
            self.ignored_directories = frozenset(IGNORED_DIRECTORIES)
        else:
            self.ignored_directories = frozenset()

        if ignored_files is not None:
            self.ignored_files: frozenset[str] = frozenset(ignored_files)
        elif self.config.respect_default_filters:
            self.ignored_files = frozenset(IGNORED_FILES)
        else:
            self.ignored_files = frozenset()

        self.supported_extensions: frozenset[str] = (
            frozenset(supported_extensions)
            if supported_extensions is not None
            else frozenset(SUPPORTED_EXTENSIONS)
        )

    def should_skip_symlink(self, path: Path) -> bool:
        """Determines if a symbolic link should be skipped based on configuration.

        Args:
            path: Target path to check for symlink status.

        Returns:
            True if path is a symlink and follow_symlinks is False, False otherwise.
        """
        if self.config.follow_symlinks:
            return False
        try:
            return path.is_symlink()
        except (OSError, ValueError):
            return True

    def should_skip_directory(self, directory: Path) -> bool:
        """Determines if a directory should be skipped during repository scanning.

        Args:
            directory: Target directory Path.

        Returns:
            True if the directory is ignored, a symlink (when not followed), or hidden dot-prefixed.
        """
        if self.should_skip_symlink(directory):
            return True

        dir_name = directory.name
        if not dir_name:
            return False

        if dir_name in self.ignored_directories:
            return True

        if not self.config.include_hidden and dir_name.startswith("."):
            return True

        return False

    def should_skip_file(
        self, file_path: Path, extension: str | None = None
    ) -> bool:
        """Determines if a file should be skipped during repository scanning.

        Args:
            file_path: Target file Path.
            extension: Optional pre-computed lowercase file extension.

        Returns:
            True if the file matches ignore sets, symlink rules, or hidden file rules.
        """
        if self.should_skip_symlink(file_path):
            return True

        filename = file_path.name
        if not filename:
            return True

        if filename in self.ignored_files:
            return True

        if not self.config.include_hidden and filename.startswith("."):
            ext = extension if extension is not None else file_path.suffix.lower()
            if ext not in self.supported_extensions:
                return True

        return False

    def is_supported_source_file(
        self, file_path: Path, extension: str | None = None
    ) -> bool:
        """Checks if a file extension matches supported source code extensions.

        Args:
            file_path: Target file Path.
            extension: Optional pre-computed lowercase file extension.

        Returns:
            True if the file extension is supported, False otherwise.
        """
        ext = extension if extension is not None else file_path.suffix.lower()
        return ext in self.supported_extensions
