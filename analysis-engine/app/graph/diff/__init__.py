"""Graph diff package.

Provides the GraphDiffEngine and immutable change models for computing codebase graph delta states.
"""

from app.graph.diff.engine import GraphDiffEngine
from app.graph.diff.exceptions import GraphDiffError, InvalidGraphComparison
from app.graph.diff.models import (
    EdgeAdded,
    EdgeRemoved,
    EdgeUpdated,
    GraphDiff,
    NodeAdded,
    NodeRemoved,
    NodeUpdated,
)

__all__ = [
    "GraphDiffEngine",
    "GraphDiff",
    "NodeAdded",
    "NodeRemoved",
    "NodeUpdated",
    "EdgeAdded",
    "EdgeRemoved",
    "EdgeUpdated",
    "GraphDiffError",
    "InvalidGraphComparison",
]
