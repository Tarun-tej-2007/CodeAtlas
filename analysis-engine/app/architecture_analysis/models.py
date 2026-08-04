"""Architecture Analysis Domain Models."""

from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.architecture_analysis.enums import ArchitectureRuleType, ArchitectureSeverity


class ArchitectureIssue(BaseModel):
    """Represents a single architecture issue identified in the codebase."""

    id: str = Field(..., description="Unique identifier for the issue.")
    rule_type: ArchitectureRuleType = Field(..., description="The type of architecture rule violated.")
    severity: ArchitectureSeverity = Field(..., description="The severity level of the issue.")
    title: str = Field(..., description="Short title describing the issue.")
    description: str = Field(..., description="Detailed description of the architectural violation.")
    affected_symbols: Tuple[str, ...] = Field(default_factory=tuple, description="Symbols affected by this issue.")
    metadata: Mapping[str, Any] = Field(default_factory=dict, description="Metadata associated with the issue.")

    model_config = ConfigDict(frozen=True)

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        """Wraps metadata inside MappingProxyType to enforce read-only runtime immutability."""
        if isinstance(v, dict):
            return MappingProxyType(dict(v))
        return v


class ArchitectureSummary(BaseModel):
    """Summary of counts of architecture issues aggregated by severity."""

    total_issues: int = Field(..., ge=0, description="Total number of architectural issues.")
    info_count: int = Field(..., ge=0, description="Count of INFO severity issues.")
    low_count: int = Field(..., ge=0, description="Count of LOW severity issues.")
    medium_count: int = Field(..., ge=0, description="Count of MEDIUM severity issues.")
    high_count: int = Field(..., ge=0, description="Count of HIGH severity issues.")
    critical_count: int = Field(..., ge=0, description="Count of CRITICAL severity issues.")

    model_config = ConfigDict(frozen=True)


class ArchitectureReport(BaseModel):
    """Aggregated architecture analysis report for a project."""

    project_name: str = Field(..., description="The name of the project under analysis.")
    generated_at: datetime = Field(..., description="Timezone-aware UTC timestamp of when the report was generated.")
    issues: Tuple[ArchitectureIssue, ...] = Field(default_factory=tuple, description="The set of identified issues.")
    summary: ArchitectureSummary = Field(..., description="Aggregated summary of issue severities.")

    model_config = ConfigDict(frozen=True)

    @field_validator("generated_at", mode="after")
    @classmethod
    def validate_utc_timezone(cls, v: datetime) -> datetime:
        """Ensures generated_at has a timezone-aware UTC datetime value."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("generated_at must be a timezone-aware UTC datetime.")
        return v
