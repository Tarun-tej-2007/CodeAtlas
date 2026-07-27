"""Graph domain exceptions module.

Defines the exception hierarchy for graph modeling operations.
"""


class GraphError(Exception):
    """Base exception class for graph domain errors."""

    pass


class GraphValidationError(GraphError):
    """Raised when graph validation fails (e.g. invalid node reference)."""

    pass


class DuplicateNodeError(GraphValidationError):
    """Raised when duplicate node IDs are detected in graph construction."""

    pass


class DuplicateEdgeError(GraphValidationError):
    """Raised when duplicate edges between same source, target, and type are detected."""

    pass
