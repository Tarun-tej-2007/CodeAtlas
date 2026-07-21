"""File metadata extractor module.

Provides the FileMetadataExtractor class responsible for extracting filesystem attributes,
modification timestamps, relative pathing, and language mappings for discovered files.
"""

from datetime import datetime, timezone
from pathlib import Path

from app.scanner.constants import EXTENSION_LANGUAGE_MAP
from app.scanner.exceptions import FileAccessError
from app.scanner.models import FileMetadata


class FileMetadataExtractor:
    """Extracts filesystem metadata and maps programming languages for individual files."""

    def __init__(self) -> None:
        """Initializes the metadata extractor."""
        pass

    def extract(
        self,
        file_path: Path,
        repository_root: Path,
        extension: str | None = None,
    ) -> FileMetadata:
        """Extracts filesystem metadata for a given file relative to repository root.

        Args:
            file_path: Absolute path to the target file.
            repository_root: Absolute path to the repository root directory.
            extension: Optional pre-computed lowercase file extension.

        Returns:
            An immutable FileMetadata instance containing filesystem attributes and language info.

        Raises:
            FileAccessError: If the file cannot be accessed or stat() fails due to I/O errors.
        """
        try:
            stat_result = file_path.stat()
        except PermissionError as err:
            raise FileAccessError(
                f"Permission denied accessing metadata for '{file_path}': {err}"
            ) from err
        except (FileNotFoundError, OSError) as err:
            raise FileAccessError(
                f"Failed to retrieve filesystem status for '{file_path}': {err}"
            ) from err

        try:
            relative_path = file_path.relative_to(repository_root)
        except ValueError as err:
            raise FileAccessError(
                f"File '{file_path}' is not located inside repository root '{repository_root}': {err}"
            ) from err

        filename = file_path.name
        ext = extension if extension is not None else file_path.suffix.lower()
        size_bytes = stat_result.st_size

        try:
            modified_at = datetime.fromtimestamp(
                stat_result.st_mtime, tz=timezone.utc
            )
        except (ValueError, OverflowError, OSError):
            modified_at = datetime.fromtimestamp(0, tz=timezone.utc)

        language = EXTENSION_LANGUAGE_MAP.get(ext)

        return FileMetadata(
            path=file_path,
            relative_path=relative_path,
            filename=filename,
            extension=ext,
            size_bytes=size_bytes,
            modified_at=modified_at,
            language=language,
        )
