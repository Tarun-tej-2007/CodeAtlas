"""Dependency graph domain models module."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.graph.enums import DependencyEdgeType, DependencyNodeType


class GraphNode(BaseModel):
    """Represents a unique semantic entity node in the dependency graph."""

    id: str = Field(..., description="Unique stable identifier for the node.")
    name: str = Field(..., description="Display name of the semantic entity.")
    type: DependencyNodeType = Field(..., description="The semantic entity type.")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Extensible metadata mapping for compiler context."
    )

    model_config = ConfigDict(frozen=True)


class GraphEdge(BaseModel):
    """Represents a directed dependency relationship between two graph nodes."""

    source_id: str = Field(..., description="The source node identifier.")
    target_id: str = Field(..., description="The target node identifier.")
    type: DependencyEdgeType = Field(..., description="The type of the relationship link.")
    metadata: Dict[str, Any] = Field(
        default_factory=dict, description="Extensible metadata mapping for context (e.g. call line coordinates)."
    )

    model_config = ConfigDict(frozen=True)


class DependencyMetadata(BaseModel):
    """Contextual descriptor metadata about the overall dependency graph structure."""

    description: Optional[str] = Field(default=None, description="Optional high-level graph description.")
    version: Optional[str] = Field(default=None, description="Schema or model configuration version.")
    attributes: Dict[str, Any] = Field(
        default_factory=dict, description="Arbitrary attribute settings."
    )

    model_config = ConfigDict(frozen=True)
