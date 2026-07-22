"""Graph diff exceptions module.

Defines the exception classes for graph diffing errors.
"""


class GraphDiffError(Exception):
    """Base exception class for all graph diffing errors."""

    pass


class InvalidGraphComparison(GraphDiffError):
    """Raised when comparing graphs is structurally invalid or input graphs are malformed."""

    pass
