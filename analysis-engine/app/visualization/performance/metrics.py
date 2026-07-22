"""Visualization performance metrics module.

Defines immutable Pydantic v2 model representing execution metrics.
"""

from pydantic import BaseModel, ConfigDict, Field


class VisualizationMetrics(BaseModel):
    """Immutable model representing execution metrics for visualization generation."""

    transformation_time_ms: float = Field(default=0.0, description="Duration of the transformation stage.")
    layout_time_ms: float = Field(default=0.0, description="Duration of the layout engine computation.")
    serialization_time_ms: float = Field(default=0.0, description="Duration of the serialization stage.")
    total_time_ms: float = Field(default=0.0, description="Total duration of the visualization pipeline.")

    node_count: int = Field(default=0, ge=0, description="Total number of nodes processed.")
    edge_count: int = Field(default=0, ge=0, description="Total number of edges processed.")

    cache_hit: bool = Field(default=False, description="Whether the generation hit a cached entry.")
    cache_miss: bool = Field(default=False, description="Whether the generation missed cached entries.")

    model_config = ConfigDict(frozen=True)
