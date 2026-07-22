"""Graph layout engine exceptions module.

Defines the exception hierarchy for graph layout computation errors.
"""


class LayoutEngineError(Exception):
    """Base exception class for all graph layout engine errors."""

    pass


class InvalidLayoutGraph(LayoutEngineError):
    """Raised when a graph is structurally malformed or invalid for layout computation."""

    pass


class CyclicLayoutError(LayoutEngineError):
    """Raised when a hierarchical layout strategy encounters cycles in the graph."""

    pass


class UnsupportedLayoutError(LayoutEngineError):
    """Raised when an unsupported layout strategy or configuration is requested."""

    pass
