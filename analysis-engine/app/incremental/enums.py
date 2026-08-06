"""Incremental Analysis Domain Enums Module."""

from enum import Enum


class ChangeType(str, Enum):
    """Enumeration of possible change types for a file."""

    ADDED = "added"
    MODIFIED = "modified"
    DELETED = "deleted"
    UNCHANGED = "unchanged"


class IncrementalStatus(str, Enum):
    """Enumeration of possible execution states for an incremental analysis job."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
