"""CodeAtlas repository scanner package.

Provides domain models, constants, and exceptions for codebase file structure discovery.
"""

from app.scanner.constants import (
    EXTENSION_LANGUAGE_MAP,
    IGNORED_DIRECTORIES,
    IGNORED_FILES,
    SUPPORTED_EXTENSIONS,
)
from app.scanner.exceptions import (
    FileAccessError,
    InvalidRepositoryError,
    RepositoryNotFoundError,
    ScannerError,
    UnsupportedLanguageError,
)
from app.scanner.models import (
    DirectoryMetadata,
    FileMetadata,
    ScanResult,
    ScanStatistics,
)

__all__ = [
    # Models
    "FileMetadata",
    "DirectoryMetadata",
    "ScanStatistics",
    "ScanResult",
    # Exceptions
    "ScannerError",
    "RepositoryNotFoundError",
    "InvalidRepositoryError",
    "UnsupportedLanguageError",
    "FileAccessError",
    # Constants
    "SUPPORTED_EXTENSIONS",
    "EXTENSION_LANGUAGE_MAP",
    "IGNORED_DIRECTORIES",
    "IGNORED_FILES",
]
