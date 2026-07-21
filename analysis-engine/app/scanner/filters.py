"""Scan filtering and exclusion module.

Provides the FilteringEngine class responsible for evaluating whether files
or directories should be traversed, processed, or skipped.
"""

from pathlib import Path

from app.scanner.constants import (
    IGNORED_DIRECTORIES,
    IGNORED_FILES,
    SUPPORTED_EXTENSIONS,
)


class FilteringEngine:
    """Evaluates whether directories and files should be processed or excluded."""

    def __init__(
        self,
        ignored_directories: set[str] | None = None,
        ignored_files: set[str] | None = None,
        supported_extensions: set[str] | None = None,
    ) -> None:
        """Initializes the filtering engine with default or custom filter sets.

        Args:
            ignored_directories: Set of directory names to ignore. Defaults to IGNORED_DIRECTORIES.
            ignored_files: Set of filenames to ignore. Defaults to IGNORED_FILES.
            supported_extensions: Set of supported file extensions. Defaults to SUPPORTED_EXTENSIONS.
        """
        self.ignored_directories = (
            ignored_directories
            if ignored_directories is not None
            else set(IGNORED_DIRECTORIES)
        )
        self.ignored_files = (
            ignored_files if ignored_files is not None else set(IGNORED_FILES)
        )
        self.supported_extensions = (
            supported_extensions
            if supported_extensions is not None
            else set(SUPPORTED_EXTENSIONS)
        )

    def should_skip_directory(self, directory: Path) -> bool:
        """Determines if a directory should be skipped during repository scanning.

        Args:
            directory: Target directory Path.

        Returns:
            True if the directory is ignored or hidden dot-prefixed, False otherwise.
        """
        dir_name = directory.name
        if not dir_name:
            return False

        if dir_name in self.ignored_directories or dir_name.startswith("."):
            return True

        return False

    def should_skip_file(self, file_path: Path) -> bool:
        """Determines if a file should be skipped during repository scanning.

        Args:
            file_path: Target file Path.

        Returns:
            True if the file matches ignore sets or hidden file rules, False otherwise.
        """
        filename = file_path.name
        if not filename:
            return True

        if filename in self.ignored_files:
            return True

        if filename.startswith("."):
            extension = file_path.suffix.lower()
            if extension not in self.supported_extensions:
                return True

        return False

    def is_supported_source_file(self, file_path: Path) -> bool:
        """Checks if a file extension matches supported source code extensions.

        Args:
            file_path: Target file Path.

        Returns:
            True if the file extension is supported, False otherwise.
        """
        extension = file_path.suffix.lower()
        return extension in self.supported_extensions
