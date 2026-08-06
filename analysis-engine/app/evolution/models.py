"""Domain DTO models for the Architecture Evolution subsystem."""

import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.evolution.enums import ArchitecturalChangeType, EvolutionStatus, RiskSeverity


class ArchitecturalChange(BaseModel):
    """Immutable model representing a modification delta in an architectural component."""

    change_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique change tracking identifier.")
    component_name: str = Field(..., min_length=1, description="Normalized name of the architectural component.")
    change_type: ArchitecturalChangeType = Field(..., description="Classification category of the change.")
    description: str = Field(default="", description="Descriptive context explaining what changed.")
    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible contextual attribute mapping metadata."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("component_name", mode="after")
    @classmethod
    def validate_component_name(cls, v: str) -> str:
        """Ensures component name is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("component_name must be a non-empty string.")
        return v

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        """Enforces immutable view protection on metadata mappings."""
        return MappingProxyType(dict(v))

    @field_serializer("metadata")
    def serialize_metadata(self, metadata: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(metadata)


class ArchitectureSnapshot(BaseModel):
    """Immutable snapshot capturing the structural composition of the codebase at a specific point."""

    snapshot_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique snapshot tracking identifier.")
    commit_id: str = Field(..., min_length=1, description="Target Git commit hash identifier representing structure.")
    timestamp: datetime = Field(..., description="UTC timezone-aware timestamp representing snapshot creation.")
    layers: Tuple[str, ...] = Field(default_factory=tuple, description="Sorted architectural layer boundaries.")
    components: Mapping[str, Any] = Field(
        default_factory=dict, description="Normalized components mapping dictionary representation."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("commit_id", mode="after")
    @classmethod
    def validate_commit_id(cls, v: str) -> str:
        """Ensures commit ID hash is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("commit_id must be a non-empty string.")
        return v

    @field_validator("timestamp", mode="after")
    @classmethod
    def validate_timestamp_timezone(cls, v: datetime) -> datetime:
        """Guarantees snapshot creation timestamps are timezone-aware UTC dates."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("timestamp must be a timezone-aware UTC datetime.")
        return v

    @field_validator("components", mode="after")
    @classmethod
    def freeze_components(cls, v: Any) -> Any:
        """Enforces immutable view protection on component mappings."""
        return MappingProxyType(dict(v))

    @field_serializer("components")
    def serialize_components(self, components: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(components)


class EvolutionSummary(BaseModel):
    """Immutable numerical statistics summary of modification categories across compared snapshots."""

    added_count: int = Field(default=0, ge=0, description="Total architectural components added.")
    removed_count: int = Field(default=0, ge=0, description="Total architectural components removed.")
    modified_count: int = Field(default=0, ge=0, description="Total architectural components modified.")
    unchanged_count: int = Field(default=0, ge=0, description="Total architectural components unchanged.")

    model_config = ConfigDict(frozen=True)


class EvolutionMetadata(BaseModel):
    """Immutable metadata descriptor tracking project scope and execution status of the analysis."""

    project_name: str = Field(..., min_length=1, description="Associated codebase project identifier name.")
    source_commit: str = Field(..., min_length=1, description="Base source commit hash.")
    target_commit: str = Field(..., min_length=1, description="Target comparison commit hash.")
    created_at: datetime = Field(..., description="UTC timezone-aware timestamp representing metadata creation.")
    status: EvolutionStatus = Field(..., description="Execution status classification.")
    extra_info: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible contextual attribute mapping metadata."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("project_name", "source_commit", "target_commit", mode="after")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validates that scope string parameters are non-empty."""
        if not v or not v.strip():
            raise ValueError("Value must be a non-empty string.")
        return v

    @field_validator("created_at", mode="after")
    @classmethod
    def validate_created_at_timezone(cls, v: datetime) -> datetime:
        """Ensures created_at timestamp is timezone-aware and set to UTC timezone."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("created_at must be a timezone-aware UTC datetime.")
        return v

    @field_validator("extra_info", mode="after")
    @classmethod
    def freeze_extra_info(cls, v: Any) -> Any:
        """Enforces immutable view protection on extra_info mappings."""
        return MappingProxyType(dict(v))

    @field_serializer("extra_info")
    def serialize_extra_info(self, extra_info: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(extra_info)


class EvolutionResult(BaseModel):
    """Immutable resulting domain object detailing complete architectural modifications and metrics."""

    evolution_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique result tracking identifier.")
    metadata: EvolutionMetadata = Field(..., description="Associated metadata parameters context.")
    changes: Tuple[ArchitecturalChange, ...] = Field(
        default_factory=tuple, description="Immutable tuple collection of component changes."
    )
    summary: EvolutionSummary = Field(..., description="Summary delta statistics values.")

    model_config = ConfigDict(frozen=True)


class EvolutionRequest(BaseModel):
    """Immutable parameter DTO payload requesting architecture evolution computation."""

    project_id: uuid.UUID = Field(..., description="Unique tracking identifier of project scope.")
    project_name: str = Field(..., min_length=1, description="Associated codebase project identifier name.")
    source_commit: str = Field(..., min_length=1, description="Baseline source commit hash.")
    target_commit: str = Field(..., min_length=1, description="Target comparison commit hash.")
    correlation_id: Optional[str] = Field(default=None, description="Optional correlation tracking identifier.")

    model_config = ConfigDict(frozen=True)

    @field_validator("project_name", "source_commit", "target_commit", mode="after")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validates that request string parameters are non-empty."""
        if not v or not v.strip():
            raise ValueError("Value must be a non-empty string.")
        return v


class EvolutionTrendResult(BaseModel):
    """Immutable model representing computed evolution trends across multiple analysis commits."""

    coupling_trend: Tuple[float, ...] = Field(default_factory=tuple, description="Trend list of coupling values.")
    complexity_trend: Tuple[float, ...] = Field(default_factory=tuple, description="Trend list of complexity values.")
    tech_debt_trend: Tuple[int, ...] = Field(default_factory=tuple, description="Trend list of tech debt item counts.")
    quality_trend: Tuple[float, ...] = Field(default_factory=tuple, description="Trend list of overall quality scores.")
    layer_stability: Tuple[float, ...] = Field(default_factory=tuple, description="Trend list of layer counts.")
    module_growth: Tuple[int, ...] = Field(default_factory=tuple, description="Accumulated module count trend.")
    summary: Mapping[str, Any] = Field(
        default_factory=dict, description="Summary mapping of overall trend indicators."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("summary", mode="after")
    @classmethod
    def freeze_summary(cls, v: Any) -> Any:
        """Enforces runtime read-only dictionary mapping properties."""
        return MappingProxyType(dict(v))

    @field_serializer("summary")
    def serialize_summary(self, summary: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(summary)


class ArchitecturalRisk(BaseModel):
    """Immutable model representing an identified architectural risk with descriptive severity classification."""

    risk_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique risk tracking identifier.")
    name: str = Field(..., min_length=1, description="Unique name/key of the architectural risk.")
    description: str = Field(..., description="Details and context explaining the risk finding.")
    score: float = Field(..., ge=0.0, le=100.0, description="Numerical risk score between 0.0 and 100.0.")
    severity: RiskSeverity = Field(..., description="Risk severity tier level.")
    mitigation_recommendation: str = Field(..., description="Actionable recommendations to resolve or mitigate the risk.")
    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible metadata properties."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        """Enforces runtime read-only dictionary mapping properties."""
        return MappingProxyType(dict(v))

    @field_serializer("metadata")
    def serialize_metadata(self, metadata: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(metadata)


class ArchitecturalRiskReport(BaseModel):
    """Immutable report aggregating all identified architectural risks and computing an overall metric."""

    report_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique report identifier.")
    generated_at: datetime = Field(..., description="UTC timezone-aware generation timestamp.")
    overall_risk_score: float = Field(..., ge=0.0, le=100.0, description="Aggregated overall risk score.")
    risks: Tuple[ArchitecturalRisk, ...] = Field(default_factory=tuple, description="Sorted tuple of detected risks.")
    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible metadata properties."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("generated_at", mode="after")
    @classmethod
    def validate_generated_at_timezone(cls, v: datetime) -> datetime:
        """Ensures generated_at timestamp is timezone-aware and set to UTC."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("generated_at must be a timezone-aware UTC datetime.")
        return v

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        """Enforces runtime read-only dictionary mapping properties."""
        return MappingProxyType(dict(v))

    @field_serializer("metadata")
    def serialize_metadata(self, metadata: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(metadata)


class ArchitectureEvolutionResult(BaseModel):
    """Immutable model representing the complete aggregated result of the architecture evolution orchestration run."""

    evolution_result_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique aggregate result identifier.")
    request: EvolutionRequest = Field(..., description="Evolution analysis query request parameters.")
    current_snapshot: ArchitectureSnapshot = Field(..., description="Calculated snapshot representing updated state.")
    previous_snapshot: Optional[ArchitectureSnapshot] = Field(default=None, description="Injected baseline snapshot representing source point.")
    changes: Tuple[ArchitecturalChange, ...] = Field(default_factory=tuple, description="Differences change log entries list.")
    summary: EvolutionSummary = Field(..., description="Aggregate changes counters summary.")
    trends: Optional[EvolutionTrendResult] = Field(default=None, description="Emerging trends metrics output data.")
    risk_report: Optional[ArchitecturalRiskReport] = Field(default=None, description="Identified architectural risks list report.")
    extra_info: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible contextual attribute mapping metadata."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("extra_info", mode="after")
    @classmethod
    def freeze_extra_info(cls, v: Any) -> Any:
        """Enforces runtime protection on extra_info mappings."""
        return MappingProxyType(dict(v))

    @field_serializer("extra_info")
    def serialize_extra_info(self, extra_info: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(extra_info)
