"""Repository acquisition exception definitions."""


class RepositoryAcquisitionError(Exception):
    """Base exception class for all repository acquisition errors."""

    pass


class RepositoryNotFoundError(RepositoryAcquisitionError):
    """Raised when the specified repository source cannot be found."""

    pass


class RepositoryCloneError(RepositoryAcquisitionError):
    """Raised when a git clone process execution fails."""

    pass


class InvalidRepositorySourceError(RepositoryAcquisitionError):
    """Raised when the provided repository source format or path is invalid."""

    pass


class RepositoryCopyError(RepositoryAcquisitionError):
    """Raised when copying a local repository fails due to OS or permission errors."""

    pass
