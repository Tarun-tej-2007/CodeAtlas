"""Workspace exceptions module.

Defines domain-specific workspace execution and filesystem exceptions.
"""


class WorkspaceError(Exception):
    """Base exception class for all workspace management errors."""

    pass


class WorkspaceAlreadyExistsError(WorkspaceError):
    """Raised when trying to create a workspace directory that already exists."""

    pass


class WorkspaceNotFoundError(WorkspaceError):
    """Raised when operations are performed on a non-existent workspace directory."""

    pass


class WorkspaceCreationError(WorkspaceError):
    """Raised when filesystem directory creation fails due to OS or permission errors."""

    pass


class WorkspaceCleanupError(WorkspaceError):
    """Raised when recursive deletion of workspace contents fails."""

    pass
