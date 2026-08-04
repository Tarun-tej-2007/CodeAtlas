"""Quality Analysis Domain Models module."""

from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Dict, Mapping, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.quality_analysis.enums import MetricCategory, QualityLevel


class QualityMetric(BaseModel):
    """Immutable model representing an individual software quality metric."""

    name: str = Field(..., min_length=1, description="Unique identifier for the metric.")
    category: MetricCategory = Field(..., description="The category this metric belongs to.")
    value: float = Field(..., description="The calculated numerical value of the metric.")
    level: QualityLevel = Field(..., description="The evaluated quality level category.")
    description: str = Field(default="", description="Descriptive explanation of the metric.")
    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible metadata properties."
    )

    model_config = ConfigDict(frozen=True)

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        """Enforces runtime read-only dictionary mapping properties."""
        return MappingProxyType(dict(v))


class QualitySummary(BaseModel):
    """Immutable model containing aggregate statistics and overall levels."""

    overall_score: float = Field(..., description="Aggregated overall quality score.")
    overall_level: QualityLevel = Field(..., description="Overall evaluated quality level.")
    metrics_by_category: Mapping[MetricCategory, float] = Field(
        default_factory=dict, description="Average values segmented by MetricCategory."
    )
    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible summary metadata."
    )

    model_config = ConfigDict(frozen=True)

    @field_validator("metrics_by_category", mode="after")
    @classmethod
    def freeze_metrics_by_category(cls, v: Any) -> Any:
        """Enforces runtime read-only dictionary mapping properties."""
        return MappingProxyType(dict(v))

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        """Enforces runtime read-only dictionary mapping properties."""
        return MappingProxyType(dict(v))


class QualityReport(BaseModel):
    """Immutable model representing a complete codebase quality report."""

    project_name: str = Field(..., min_length=1, description="Name of the analyzed project.")
    generated_at: datetime = Field(..., description="Timezone-aware UTC timestamp when report was generated.")
    metrics: Tuple[QualityMetric, ...] = Field(
        default_factory=tuple, description="Sorted tuple of calculated metrics."
    )
    summary: QualitySummary = Field(..., description="Aggregated quality summary data.")
    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible report configuration details."
    )

    model_config = ConfigDict(frozen=True)

    @field_validator("generated_at", mode="after")
    @classmethod
    def validate_utc_timestamp(cls, v: datetime) -> datetime:
        """Validates that the timestamp is timezone-aware and set to UTC."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("generated_at must be a timezone-aware UTC datetime.")
        return v

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        """Enforces runtime read-only dictionary mapping properties."""
        return MappingProxyType(dict(v))
