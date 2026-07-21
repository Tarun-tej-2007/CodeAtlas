"""CodeAtlas graph query package.

Provides GraphQueryEngine, filter functions, and exception classes for O(1) and O(degree)
graph querying and structural/behavioral traversals.
"""

from app.graph.query.exceptions import GraphQueryError
from app.graph.query.filters import filter_edges, filter_nodes
from app.graph.query.query_engine import GraphQueryEngine


__all__ = [
    # Exceptions
    "GraphQueryError",
    # Filters
    "filter_nodes",
    "filter_edges",
    # Query Engine
    "GraphQueryEngine",
]
