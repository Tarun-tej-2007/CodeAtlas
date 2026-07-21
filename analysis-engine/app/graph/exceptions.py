"""Graph domain exceptions module.

Defines the exception hierarchy for graph modeling and graph building operations.
"""


class GraphError(Exception):
    """Base exception class for graph domain errors."""

    pass


class GraphBuilderError(GraphError):
    """Raised when a graph builder pass encounters unrecoverable errors."""

    pass
