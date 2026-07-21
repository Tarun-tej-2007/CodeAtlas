"""Visualization presentation style models module.

Defines renderer-agnostic, immutable presentation hint models for visualization nodes,
edges, and groups.
"""

from pydantic import BaseModel, ConfigDict, Field


class NodeStyle(BaseModel):
    """Represents presentation styling hints for visualization nodes."""

    shape: str = Field(default="default", description="Node shape presentation hint.")
    icon: str | None = Field(default=None, description="Optional icon identifier or SVG symbol name.")
    color: str | None = Field(default=None, description="Primary fill or background color.")
    border_color: str | None = Field(default=None, description="Border or stroke color.")
    border_width: float = Field(default=1.0, gt=0, description="Border width in pixels (must be > 0).")

    model_config = ConfigDict(frozen=True)


class EdgeStyle(BaseModel):
    """Represents presentation styling hints for visualization edges."""

    width: float = Field(default=1.0, gt=0, description="Edge line width in pixels (must be > 0).")
    style: str = Field(default="solid", description="Line stroke style hint (e.g. solid, dashed, dotted).")
    arrow: bool = Field(default=True, description="Whether to display a target directional arrowhead.")
    color: str | None = Field(default=None, description="Edge stroke color.")

    model_config = ConfigDict(frozen=True)


class GroupStyle(BaseModel):
    """Represents presentation styling hints for visualization groups."""

    background_color: str | None = Field(default=None, description="Group bounding box background fill color.")
    border_color: str | None = Field(default=None, description="Group bounding box border color.")
    border_width: float = Field(default=1.0, gt=0, description="Border width in pixels (must be > 0).")
    collapsed: bool = Field(default=False, description="Whether the group container is collapsed by default.")

    model_config = ConfigDict(frozen=True)
