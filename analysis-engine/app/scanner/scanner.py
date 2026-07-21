"""Codebase repository scanner module.

Provides the Scanner class for recursive repository directory traversal,
supported source file discovery, and scan statistics aggregation.
"""

from datetime import datetime, timezone
from pathlib import Path
import time

from app.scanner.constants import EXTENSION_LANGUAGE_MAP, SUPPORTED_EXTENSIONS
from app.scanner.exceptions import (
    FileAccessError,
    InvalidRepositoryError,
    RepositoryNotFoundError,
)
from app.scanner.models import (
    DirectoryMetadata,
    FileMetadata,
    ScanResult,
    ScanStatistics,
)


class Scanner:
    """Recursively scans a repository root directory for source files and structure."""

    def __init__(self, repository_root: Path | str) -> None:
        """Initializes and validates the repository scanner.

        Args:
            repository_root: Absolute or relative path to the target repository root.

        Raises:
            RepositoryNotFoundError: If the repository root path does not exist.
            InvalidRepositoryError: If the repository root path is not a directory.
            FileAccessError: If filesystem permissions prevent accessing the repository path.
        """
        try:
            self.repository_root = Path(repository_root).resolve()
        except Exception as err:
            raise InvalidRepositoryError(
                f"Failed to resolve repository path '{repository_root}': {err}"
            ) from err

        try:
            if not self.repository_root.exists():
                raise RepositoryNotFoundError(
                    f"Repository root directory does not exist: {self.repository_root}"
                )
            if not self.repository_root.is_dir():
                raise InvalidRepositoryError(
                    f"Repository root path is not a directory: {self.repository_root}"
                )
        except (RepositoryNotFoundError, InvalidRepositoryError):
            raise
        except PermissionError as err:
            raise FileAccessError(
                f"Permission denied accessing repository root '{self.repository_root}': {err}"
            ) from err
        except OSError as err:
            raise InvalidRepositoryError(
                f"Inaccessible repository root '{self.repository_root}': {err}"
            ) from err

    def scan(self) -> ScanResult:
        """Recursively scans the repository for directories and supported source files.

        Returns:
            ScanResult containing discovered file metadata, directory structure,
            and aggregate scan statistics.

        Raises:
            FileAccessError: If filesystem traversal encounters unrecoverable I/O errors.
        """
        start_time = time.monotonic()

        directories: list[DirectoryMetadata] = []
        files: list[FileMetadata] = []

        total_files_count = 0
        source_files_count = 0
        ignored_files_count = 0

        # Include repository root directory (depth 0)
        directories.append(
            DirectoryMetadata(
                path=self.repository_root,
                relative_path=Path("."),
                depth=0,
            )
        )

        try:
            # Walk directory tree using Python 3.12 pathlib Path.walk()
            for current_root, dir_names, file_names in self.repository_root.walk():
                # Process child directories
                for dir_name in sorted(dir_names):
                    dir_path = current_root / dir_name
                    rel_dir_path = dir_path.relative_to(self.repository_root)
                    depth = len(rel_dir_path.parts)
                    directories.append(
                        DirectoryMetadata(
                            path=dir_path,
                            relative_path=rel_dir_path,
                            depth=depth,
                        )
                    )

                # Process child files
                for file_name in sorted(file_names):
                    total_files_count += 1
                    file_path = current_root / file_name
                    extension = file_path.suffix.lower()

                    if extension in SUPPORTED_EXTENSIONS:
                        source_files_count += 1
                        rel_file_path = file_path.relative_to(self.repository_root)
                        language = EXTENSION_LANGUAGE_MAP.get(extension)

                        # Placeholders for size_bytes and modified_at (Populated in Step 3)
                        file_metadata = FileMetadata(
                            path=file_path,
                            relative_path=rel_file_path,
                            filename=file_name,
                            extension=extension,
                            size_bytes=0,  # Placeholder: Populated during Step 3 metadata extraction
                            modified_at=datetime.fromtimestamp(0, tz=timezone.utc),  # Placeholder: Populated during Step 3
                            language=language,
                        )
                        files.append(file_metadata)
                    else:
                        ignored_files_count += 1

        except PermissionError as err:
            raise FileAccessError(
                f"Permission denied during repository scan at '{self.repository_root}': {err}"
            ) from err
        except OSError as err:
            raise FileAccessError(
                f"I/O error during repository scan at '{self.repository_root}': {err}"
            ) from err

        # Ensure deterministic ordering by sorting paths
        directories.sort(key=lambda d: d.path)
        files.sort(key=lambda f: f.path)

        scan_duration_ms = round((time.monotonic() - start_time) * 1000, 2)

        statistics = ScanStatistics(
            total_files=total_files_count,
            source_files=source_files_count,
            ignored_files=ignored_files_count,
            directories=len(directories),
            scan_duration_ms=scan_duration_ms,
        )

        return ScanResult(
            repository_root=self.repository_root,
            files=files,
            directories=directories,
            statistics=statistics,
        )
