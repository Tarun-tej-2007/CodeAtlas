"""Domain DTO models for the Architecture Evolution subsystem."""

import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.evolution.enums import ArchitecturalChangeType, EvolutionStatus


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

    model_config = ConfigDict(frozen=True)

    @field_validator("project_name", "source_commit", "target_commit", mode="after")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validates that request string parameters are non-empty."""
        if not v or not v.strip():
            raise ValueError("Value must be a non-empty string.")
        return v
