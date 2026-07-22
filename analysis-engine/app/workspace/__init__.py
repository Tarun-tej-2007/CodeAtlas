"""Workspace management domain package.

Provides WorkspaceManager, Workspace models, and workspace lifecycle exception classes.
"""

from app.workspace.exceptions import (
    WorkspaceAlreadyExistsError,
    WorkspaceCleanupError,
    WorkspaceCreationError,
    WorkspaceError,
    WorkspaceNotFoundError,
)
from app.workspace.manager import WorkspaceManager
from app.workspace.models import Workspace

__all__ = [
    # Models
    "Workspace",
    # Manager
    "WorkspaceManager",
    # Exceptions
    "WorkspaceError",
    "WorkspaceAlreadyExistsError",
    "WorkspaceNotFoundError",
    "WorkspaceCreationError",
    "WorkspaceCleanupError",
]
