"""Graph diff models module.

Defines immutable Pydantic v2 change models representing added, removed,
and updated nodes and edges between two graph states.
"""

from pydantic import BaseModel, ConfigDict, Field
from app.graph.models import GraphEdge, GraphNode


class NodeAdded(BaseModel):
    """Represents a node added in the new graph."""

    id: str = Field(..., description="Unique ID of the added node.")
    node: GraphNode = Field(..., description="The added GraphNode model.")

    model_config = ConfigDict(frozen=True)


class NodeRemoved(BaseModel):
    """Represents a node removed from the old graph."""

    id: str = Field(..., description="Unique ID of the removed node.")
    node: GraphNode = Field(..., description="The removed GraphNode model.")

    model_config = ConfigDict(frozen=True)


class NodeUpdated(BaseModel):
    """Represents a node whose properties were updated."""

    id: str = Field(..., description="Unique ID of the updated node.")
    old_node: GraphNode = Field(..., description="The node properties before the change.")
    new_node: GraphNode = Field(..., description="The node properties after the change.")

    model_config = ConfigDict(frozen=True)


class EdgeAdded(BaseModel):
    """Represents an edge added in the new graph."""

    id: str = Field(..., description="Unique ID of the added edge.")
    edge: GraphEdge = Field(..., description="The added GraphEdge model.")

    model_config = ConfigDict(frozen=True)


class EdgeRemoved(BaseModel):
    """Represents an edge removed from the old graph."""

    id: str = Field(..., description="Unique ID of the removed edge.")
    edge: GraphEdge = Field(..., description="The removed GraphEdge model.")

    model_config = ConfigDict(frozen=True)


class EdgeUpdated(BaseModel):
    """Represents an edge whose properties were updated."""

    id: str = Field(..., description="Unique ID of the updated edge.")
    old_edge: GraphEdge = Field(..., description="The edge properties before the change.")
    new_edge: GraphEdge = Field(..., description="The edge properties after the change.")

    model_config = ConfigDict(frozen=True)


class GraphDiff(BaseModel):
    """Aggregates all change sets comparing old and new graph states."""

    nodes_added: tuple[NodeAdded, ...] = Field(default=(), description="Nodes added in the new graph.")
    nodes_removed: tuple[NodeRemoved, ...] = Field(default=(), description="Nodes removed in the new graph.")
    nodes_updated: tuple[NodeUpdated, ...] = Field(default=(), description="Nodes updated in the new graph.")

    edges_added: tuple[EdgeAdded, ...] = Field(default=(), description="Edges added in the new graph.")
    edges_removed: tuple[EdgeRemoved, ...] = Field(default=(), description="Edges removed in the new graph.")
    edges_updated: tuple[EdgeUpdated, ...] = Field(default=(), description="Edges updated in the new graph.")

    model_config = ConfigDict(frozen=True)
