"""CodeAtlas graph domain package.

Provides canonical graph models (GraphNode, GraphEdge, GraphMetadata), enums (NodeType, EdgeType),
Graph container, and graph exception classes.
Also provides DependencyGraph and its models for dependency graph operations.
"""

from app.graph.enums import (
    EdgeType,
    NodeType,
    DependencyEdgeType,
    DependencyNodeType,
)
from app.graph.exceptions import (
    GraphError,
    GraphValidationError,
    DuplicateNodeError,
    DuplicateEdgeError,
)
from app.graph.graph import Graph
from app.graph.models import GraphEdge, GraphMetadata, GraphNode
from app.graph.query import GraphQueryEngine, GraphQueryError
from app.graph.serialization import GraphSerializationError, GraphSerializer
from app.graph.diff import (
    GraphDiffEngine,
    GraphDiff,
    GraphDiffError,
    InvalidGraphComparison,
)
from app.graph.dependency_models import DependencyMetadata
from app.graph.dependency_graph import DependencyGraph
from app.graph.dependency_builder import DependencyGraphBuilder
from app.graph.call_graph_builder import CallGraphBuilder
from app.graph.cycle_detector import CycleResult, CycleDetector
from app.graph.scc import SCCResult, SCCEngine

__all__ = [
    # Enums
    "NodeType",
    "EdgeType",
    "DependencyNodeType",
    "DependencyEdgeType",
    # Models
    "GraphNode",
    "GraphEdge",
    "GraphMetadata",
    "DependencyMetadata",
    "DependencyGraph",
    "CycleResult",
    "SCCResult",
    # Exceptions
    "GraphError",
    "GraphValidationError",
    "DuplicateNodeError",
    "DuplicateEdgeError",
    "GraphQueryError",
    "GraphSerializationError",
    # Graph Container, Query Engine & Serializer
    "Graph",
    "GraphQueryEngine",
    "GraphSerializer",
    # Diff Engine
    "GraphDiffEngine",
    "GraphDiff",
    "GraphDiffError",
    "InvalidGraphComparison",
    # Dependency Graph Builder & Call Graph Builder
    "DependencyGraphBuilder",
    "CallGraphBuilder",
    # Cycle Detection & SCC Engine
    "CycleDetector",
    "SCCEngine",
]
