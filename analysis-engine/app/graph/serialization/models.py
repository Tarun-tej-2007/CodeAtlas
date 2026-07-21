"""Serialized graph domain schema module.

Defines the SerializedGraph Pydantic v2 model representing portable JSON/dict representations
of a CodeAtlas Graph container.
"""

from pydantic import BaseModel, ConfigDict, Field
from app.graph.models import GraphEdge, GraphMetadata, GraphNode


class SerializedGraph(BaseModel):
    """Immutable representation of a serialized graph including metadata, nodes, and edges."""

    metadata: GraphMetadata = Field(..., description="GraphMetadata model.")
    nodes: list[GraphNode] = Field(default_factory=list, description="Ordered list of GraphNode objects.")
    edges: list[GraphEdge] = Field(default_factory=list, description="Ordered list of GraphEdge objects.")

    model_config = ConfigDict(frozen=True)
