"""CodeAtlas graph domain package.

Provides canonical graph models (GraphNode, GraphEdge, GraphMetadata), enums (NodeType, EdgeType),
Graph container, BaseGraphBuilder interface, and graph exception classes.
"""

from app.graph.builder import BaseGraphBuilder
from app.graph.builders import CallGraphBuilder, SymbolGraphBuilder
from app.graph.enums import EdgeType, NodeType
from app.graph.exceptions import GraphBuilderError, GraphError
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
    "GraphBuilderError",
    "GraphQueryError",
    "GraphSerializationError",
    # Graph Container, Builders, Query Engine & Serializer
    "Graph",
    "BaseGraphBuilder",
    "SymbolGraphBuilder",
    "CallGraphBuilder",
    "GraphQueryEngine",
    "GraphSerializer",
]




