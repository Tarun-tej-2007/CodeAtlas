"""Visualization domain models module.

Defines renderer-agnostic, immutable Pydantic v2 models for visualization nodes,
edges, groups, positions, metadata, and the aggregate VisualizationGraph.
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.visualization.enums import EdgeKind, GroupKind, LayoutKind, NodeKind
from app.visualization.styles import EdgeStyle, GroupStyle, NodeStyle


class Position(BaseModel):
    """Represents a 2D node position within a visualization layout."""

    x: float = Field(..., description="X-coordinate floating point value.")
    y: float = Field(..., description="Y-coordinate floating point value.")

    model_config = ConfigDict(frozen=True)


class VisualizationNode(BaseModel):
    """Represents a renderable visualization node entity."""

    id: str = Field(..., description="Unique identifier for the visualization node.")
    label: str = Field(..., description="Human-readable display label.")
    kind: NodeKind = Field(..., description="Node category classification.")
    position: Position | None = Field(default=None, description="Optional 2D spatial position.")
    style: NodeStyle = Field(default_factory=NodeStyle, description="Presentation styling hints.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata attributes.")

    model_config = ConfigDict(frozen=True)


class VisualizationEdge(BaseModel):
    """Represents a renderable visualization directional edge entity."""

    id: str = Field(..., description="Unique identifier for the visualization edge.")
    source: str = Field(..., description="Source visualization node ID.")
    target: str = Field(..., description="Target visualization node ID.")
    kind: EdgeKind = Field(..., description="Edge category classification.")
    style: EdgeStyle = Field(default_factory=EdgeStyle, description="Presentation styling hints.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata attributes.")

    model_config = ConfigDict(frozen=True)


class VisualizationGroup(BaseModel):
    """Represents a logical grouping container of visualization nodes."""

    id: str = Field(..., description="Unique identifier for the visualization group.")
    label: str = Field(..., description="Human-readable group label.")
    kind: GroupKind = Field(..., description="Group category classification.")
    members: tuple[str, ...] = Field(default=(), description="Immutable tuple of member node IDs.")
    style: GroupStyle = Field(default_factory=GroupStyle, description="Presentation styling hints.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata attributes.")

    model_config = ConfigDict(frozen=True)


class VisualizationMetadata(BaseModel):
    """Metadata describing summary analytics for a visualization graph."""

    node_count: int = Field(default=0, ge=0, description="Total node count (must be >= 0).")
    edge_count: int = Field(default=0, ge=0, description="Total edge count (must be >= 0).")
    group_count: int = Field(default=0, ge=0, description="Total group count (must be >= 0).")
    layout: LayoutKind = Field(default=LayoutKind.NONE, description="Applied graph layout strategy.")
    graph_version: str = Field(default="1.0", description="Visualization graph schema version.")

    model_config = ConfigDict(frozen=True)


class VisualizationGraph(BaseModel):
    """Aggregate root representing the complete renderable visualization model."""

    nodes: tuple[VisualizationNode, ...] = Field(default=(), description="Immutable tuple of visualization nodes.")
    edges: tuple[VisualizationEdge, ...] = Field(default=(), description="Immutable tuple of visualization edges.")
    groups: tuple[VisualizationGroup, ...] = Field(default=(), description="Immutable tuple of visualization groups.")
    metadata: VisualizationMetadata = Field(
        default_factory=VisualizationMetadata,
        description="Visualization summary metadata.",
    )

    model_config = ConfigDict(frozen=True)
