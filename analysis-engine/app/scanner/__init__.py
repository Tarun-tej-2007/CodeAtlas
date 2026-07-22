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
    FileDiscoveryError,
    DiscoveryRootNotFoundError,
    InvalidDiscoveryRootError,
    DiscoveryFailureError,
)
from app.scanner.models import (
    DirectoryMetadata,
    FileMetadata,
    ScanResult,
    ScanStatistics,
    DiscoveredFile,
    DiscoveryResult,
)

from app.scanner.config import ScannerConfig
from app.scanner.filters import FilteringEngine
from app.scanner.metadata import FileMetadataExtractor
from app.scanner.scanner import Scanner
from app.scanner.discovery import FileDiscoveryService

__all__ = [
    # Config & Pipeline Engine
    "Scanner",
    "ScannerConfig",
    "FileMetadataExtractor",
    "FilteringEngine",
    # Models
    "FileMetadata",
    "DirectoryMetadata",
    "ScanStatistics",
    "ScanResult",
    "DiscoveredFile",
    "DiscoveryResult",
    # Exceptions
    "ScannerError",
    "RepositoryNotFoundError",
    "InvalidRepositoryError",
    "UnsupportedLanguageError",
    "FileAccessError",
    "FileDiscoveryError",
    "DiscoveryRootNotFoundError",
    "InvalidDiscoveryRootError",
    "DiscoveryFailureError",
    # Constants
    "SUPPORTED_EXTENSIONS",
    "EXTENSION_LANGUAGE_MAP",
    "IGNORED_DIRECTORIES",
    "IGNORED_FILES",
    # Service
    "FileDiscoveryService",
]


