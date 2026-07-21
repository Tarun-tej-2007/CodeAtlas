"""Graph domain data models module.

Defines immutable Pydantic v2 models for GraphNode, GraphEdge, and GraphMetadata.
"""

from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.graph.enums import EdgeType, NodeType


class GraphNode(BaseModel):
    """Represents a canonical node in the CodeAtlas codebase graph."""

    id: str = Field(..., description="Unique identifier for the graph node.")
    type: NodeType = Field(..., description="Node classification type.")
    name: str = Field(..., description="Human-readable name of the entity.")
    path: Path | None = Field(default=None, description="Absolute or relative filesystem path.")
    line: int | None = Field(default=None, ge=1, description="1-indexed line number if applicable.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata attributes.")

    model_config = ConfigDict(frozen=True)


class GraphEdge(BaseModel):
    """Represents a directional relationship edge in the CodeAtlas codebase graph."""

    id: str = Field(..., description="Unique identifier for the graph edge.")
    source: str = Field(..., description="Source node ID.")
    target: str = Field(..., description="Target node ID.")
    type: EdgeType = Field(..., description="Edge relationship type.")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Arbitrary metadata attributes.")

    model_config = ConfigDict(frozen=True)


class GraphMetadata(BaseModel):
    """Metadata describing a generated graph instance."""

    project_name: str = Field(..., description="Name of the analyzed repository or project.")
    generated_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 UTC timestamp of graph generation.",
    )
    language: str = Field(default="javascript", description="Primary language context of the graph.")
    version: str = Field(default="1.0.0", description="CodeAtlas graph format schema version.")

    model_config = ConfigDict(frozen=True)

