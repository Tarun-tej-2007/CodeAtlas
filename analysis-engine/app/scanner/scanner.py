"""Codebase repository scanner module.

Provides the Scanner class for pipeline orchestration of repository traversal,
filtering, metadata extraction, and result composition.
"""

from pathlib import Path
import time

from app.scanner.config import ScannerConfig
from app.scanner.exceptions import (
    FileAccessError,
    InvalidRepositoryError,
    RepositoryNotFoundError,
)
from app.scanner.filters import FilteringEngine
from app.scanner.metadata import FileMetadataExtractor
from app.scanner.models import (
    DirectoryMetadata,
    FileMetadata,
    ScanResult,
    ScanStatistics,
)


class Scanner:
    """Orchestrates repository scanning pipeline components."""

    def __init__(
        self,
        repository_root: Path | str,
        config: ScannerConfig | None = None,
        filters: FilteringEngine | None = None,
        metadata_extractor: FileMetadataExtractor | None = None,
        extractor: FileMetadataExtractor | None = None,
    ) -> None:
        """Initializes and validates the repository scanner.

        Args:
            repository_root: Absolute or relative path to the target repository root.
            config: Optional ScannerConfig instance controlling scanning policies.
            filters: Optional FilteringEngine instance.
            metadata_extractor: Optional FileMetadataExtractor instance.
            extractor: Backward-compatible alias for metadata_extractor.

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

        self.config = config or ScannerConfig()
        self.filters = filters or FilteringEngine(config=self.config)
        self.extractor = metadata_extractor or extractor or FileMetadataExtractor()

    def scan(self) -> ScanResult:
        """Recursively scans the repository using injected pipeline components.

        Returns:
            ScanResult containing discovered file metadata, directory structure,
            and aggregate scan statistics.

        Raises:
            FileAccessError: If filesystem traversal encounters unrecoverable I/O errors.
        """
        start_time = time.monotonic() if self.config.collect_statistics else 0.0

        directories: list[DirectoryMetadata] = []
        files: list[FileMetadata] = []

        total_files_count = 0
        source_files_count = 0
        ignored_files_count = 0

        visited_real_dirs: set[Path] = {self.repository_root}

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
            for current_root, dir_names, file_names in self.repository_root.walk(
                follow_symlinks=self.config.follow_symlinks
            ):
                # Filter out ignored directories in-place and collect valid child directory metadata
                self._process_subdirectories(
                    current_root=current_root,
                    dir_names=dir_names,
                    directories=directories,
                    visited_real_dirs=visited_real_dirs,
                )

                # Process child files
                (
                    t_count,
                    s_count,
                    i_count,
                ) = self._process_files(
                    current_root=current_root,
                    file_names=file_names,
                    files=files,
                )

                total_files_count += t_count
                source_files_count += s_count
                ignored_files_count += i_count

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

        scan_duration_ms = (
            round((time.monotonic() - start_time) * 1000, 2)
            if self.config.collect_statistics
            else 0.0
        )

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

    def _process_subdirectories(
        self,
        current_root: Path,
        dir_names: list[str],
        directories: list[DirectoryMetadata],
        visited_real_dirs: set[Path],
    ) -> None:
        """Filters child directory names in-place and appends valid DirectoryMetadata."""
        valid_dir_names: list[str] = []
        for d in dir_names:
            dir_path = current_root / d
            if self.filters.should_skip_directory(dir_path):
                continue

            # Prevent infinite symlink loops when follow_symlinks is True
            if self.config.follow_symlinks:
                try:
                    real_dir_path = dir_path.resolve()
                    if real_dir_path in visited_real_dirs:
                        continue
                    visited_real_dirs.add(real_dir_path)
                except (OSError, RuntimeError):
                    continue

            valid_dir_names.append(d)

        # Mutate dir_names in-place to prevent Path.walk() from traversing skipped trees
        dir_names[:] = valid_dir_names

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

    def _process_files(
        self,
        current_root: Path,
        file_names: list[str],
        files: list[FileMetadata],
    ) -> tuple[int, int, int]:
        """Filters files, extracts metadata for supported source files, and returns count metrics."""
        total_count = 0
        source_count = 0
        ignored_count = 0

        for file_name in file_names:
            if self.config.collect_statistics:
                total_count += 1

            file_path = current_root / file_name
            extension = file_path.suffix.lower()

            if self.filters.should_skip_file(file_path, extension=extension):
                if self.config.collect_statistics:
                    ignored_count += 1
            elif self.filters.is_supported_source_file(file_path, extension=extension):
                if self.config.collect_statistics:
                    source_count += 1
                file_metadata = self.extractor.extract(
                    file_path, self.repository_root, extension=extension
                )
                files.append(file_metadata)
            else:
                if self.config.collect_statistics:
                    ignored_count += 1

        return total_count, source_count, ignored_count
