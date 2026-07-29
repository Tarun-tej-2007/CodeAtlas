"""CodeAtlas graph query package.

Provides GraphQueryEngine, filter functions, and exception classes for O(1) and O(degree)
graph querying and structural/behavioral traversals.
Also provides DependencyGraphQuery explicitly loaded from sibling query.py.
"""

import sys
import importlib.util
from pathlib import Path

from app.graph.query.exceptions import GraphQueryError
from app.graph.query.filters import filter_edges, filter_nodes
from app.graph.query.query_engine import GraphQueryEngine

# Explicitly load the sister module query.py to avoid package name conflicts
_spec = importlib.util.spec_from_file_location(
    "app.graph.query_module",
    Path(__file__).parent.parent / "query.py"
)
if _spec and _spec.loader:
    _mod = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)
    DependencyGraphQuery = getattr(_mod, "DependencyGraphQuery")
else:
    raise ImportError("Failed to locate app/graph/query.py sister module.")

__all__ = [
    # Exceptions
    "GraphQueryError",
    # Filters
    "filter_nodes",
    "filter_edges",
    # Query Engines
    "GraphQueryEngine",
    "DependencyGraphQuery",
]
