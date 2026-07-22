"""Graph builder exceptions module.

Defines exceptions raised during graph construction and enrichment pipeline passes.
"""

from app.graph.exceptions import GraphError


class GraphBuilderError(GraphError):
    """Raised when a graph builder pass encounters unrecoverable errors."""

    pass
