"""CodeAtlas graph domain package.

Provides canonical graph models (GraphNode, GraphEdge, GraphMetadata), enums (NodeType, EdgeType),
Graph container, BaseGraphBuilder interface, and graph exception classes.
"""

from app.graph.builder import BaseGraphBuilder
from app.graph.enums import EdgeType, NodeType
from app.graph.exceptions import GraphBuilderError, GraphError
from app.graph.graph import Graph
from app.graph.models import GraphEdge, GraphMetadata, GraphNode

__all__ = [
    # Enums
    "NodeType",
    "EdgeType",
    # Models
    "GraphNode",
    "GraphEdge",
    "GraphMetadata",
    # Exceptions
    "GraphError",
    "GraphBuilderError",
    # Graph Container & Base Builder
    "Graph",
    "BaseGraphBuilder",
]
