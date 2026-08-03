"""Architecture Analysis Domain Models module.

Defines frozen, immutable Pydantic models for layers, metrics,
diagnostics, and analysis results.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.architecture.enums import (
    AnalysisCategory,
    LayerType,
    SeverityLevel,
)


class ArchitectureIssue(BaseModel):
    """Represents a single structural violation, smell, or issue detected in the codebase."""

    id: str = Field(..., description="Unique identifier for this issue instance.")
    title: str = Field(..., description="Short, human-readable summary of the issue.")
    description: str = Field(..., description="Detailed explanation of the issue and its architectural impact.")
    severity: SeverityLevel = Field(..., description="The impact severity of the issue.")
    category: AnalysisCategory = Field(..., description="Classification category for the architectural issue.")
    recommendation: str = Field(..., description="Clear remediation steps or recommendations to resolve the issue.")
    location: Optional[str] = Field(None, description="Optional target location identifier, e.g. a node ID or file path.")
    metadata: Dict[str, str] = Field(default_factory=dict, description="Custom properties or contextual analysis metadata.")

    model_config = ConfigDict(frozen=True)


class ArchitectureLayer(BaseModel):
    """Represents a defined architectural layer containing specific node IDs."""

    id: str = Field(..., description="Unique identifier for the layer.")
    name: str = Field(..., description="Human-readable name of the layer.")
    layer_type: LayerType = Field(..., description="Layer type classification.")
    node_ids: List[str] = Field(
        default_factory=list, description="IDs of graph nodes grouped within this layer."
    )
    metadata: Dict[str, str] = Field(default_factory=dict, description="Layer-specific configuration or metadata.")

    model_config = ConfigDict(frozen=True)


class ArchitectureMetric(BaseModel):
    """Represents a calculated architectural metric value."""

    name: str = Field(..., description="Unique identifier name of the metric.")
    value: float = Field(..., description="Numeric value of the metric.")
    unit: str = Field(..., description="Measurement unit (e.g. 'dimensionless', 'count', 'ratio').")
    description: str = Field(..., description="Explanation of what this metric calculates and represents.")
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Contextual parameters or configurations for the calculation."
    )

    model_config = ConfigDict(frozen=True)


class ArchitectureAnalysisResult(BaseModel):
    """Container representing the complete, immutable results of an architecture analysis run."""

    issues: List[ArchitectureIssue] = Field(
        default_factory=list, description="List of all detected architecture issues."
    )
    layers: List[ArchitectureLayer] = Field(
        default_factory=list, description="List of identified architectural layers."
    )
    metrics: List[ArchitectureMetric] = Field(
        default_factory=list, description="List of computed architectural metrics."
    )
    diagnostics: List[str] = Field(
        default_factory=list, description="Diagnostic running logs or execution records."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Run-specific analysis configuration metadata."
    )

    model_config = ConfigDict(frozen=True)
