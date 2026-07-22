"""Visualization pipeline configuration module.

Defines the configuration model for selecting and styling visualization layouts.
"""

from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from app.visualization.enums import LayoutKind


class VisualizationPipelineConfig(BaseModel):
    """Configuration options for the VisualizationPipeline."""

    layout_type: LayoutKind = Field(
        default=LayoutKind.HIERARCHICAL,
        description="The layout engine algorithm strategy to apply.",
    )

    horizontal_spacing: float | None = Field(
        default=None,
        gt=0,
        description="Optional horizontal spacing override for the layout engine.",
    )

    vertical_spacing: float | None = Field(
        default=None,
        gt=0,
        description="Optional vertical spacing override for the layout engine.",
    )

    rendering_options: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional rendering or engine-specific configuration overrides.",
    )

    model_config = ConfigDict(frozen=True)
