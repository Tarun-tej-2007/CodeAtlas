"""CodeAtlas graph domain package.

Provides canonical graph models (GraphNode, GraphEdge, GraphMetadata), enums (NodeType, EdgeType),
Graph container, and graph exception classes.
"""

from app.graph.enums import EdgeType, NodeType
from app.graph.exceptions import GraphError
from app.graph.graph import Graph
from app.graph.models import GraphEdge, GraphMetadata, GraphNode
from app.graph.query import GraphQueryEngine, GraphQueryError
from app.graph.serialization import GraphSerializationError, GraphSerializer

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
    "GraphQueryError",
    "GraphSerializationError",
    # Graph Container, Query Engine & Serializer
    "Graph",
    "GraphQueryEngine",
    "GraphSerializer",
]
