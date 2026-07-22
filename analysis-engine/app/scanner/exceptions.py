"""Scanner domain exceptions module.

Defines the exception hierarchy for repository scanning operations in CodeAtlas.
"""


class ScannerError(Exception):
    """Base exception class for all codebase scanner errors."""

    pass


class RepositoryNotFoundError(ScannerError):
    """Raised when a specified repository root directory does not exist on disk."""

    pass


class InvalidRepositoryError(ScannerError):
    """Raised when a repository path is invalid, inaccessible, or not a directory."""

    pass


class UnsupportedLanguageError(ScannerError):
    """Raised when encountering an unsupported programming language or extension."""

    pass


class FileAccessError(ScannerError):
    """Raised when file permissions or I/O errors prevent file inspection."""

    pass


class FileDiscoveryError(Exception):
    """Base exception class for all file discovery errors."""

    pass


class DiscoveryRootNotFoundError(FileDiscoveryError):
    """Raised when the specified repository root directory does not exist on disk."""

    pass


class InvalidDiscoveryRootError(FileDiscoveryError):
    """Raised when a repository path is invalid, inaccessible, or not a directory."""

    pass


class DiscoveryFailureError(FileDiscoveryError):
    """Raised when recursive file traversal encounters filesystem failures."""

    pass

