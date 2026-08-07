"""Domain models for Architecture Decision Intelligence."""

import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.decision.enums import DecisionCategory, DecisionPriority, DecisionRelationshipType, DecisionStatus


class DecisionRelationship(BaseModel):
    """Immutable relationship definition between two ArchitectureDecision entities."""

    source_decision_id: uuid.UUID = Field(..., description="Unique tracking identifier of source decision.")
    target_decision_id: uuid.UUID = Field(..., description="Unique tracking identifier of target decision.")
    relationship_type: DecisionRelationshipType = Field(..., description="Relation classification link type.")

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class DecisionMetadata(BaseModel):
    """Immutable metadata descriptor attributes of an ArchitectureDecision."""

    author: str = Field(..., min_length=1, description="Decision author/creator handle.")
    created_at: datetime = Field(..., description="UTC timezone-aware timestamp when decision record was registered.")
    updated_at: datetime = Field(..., description="UTC timezone-aware timestamp when decision record was last modified.")
    tags: Tuple[str, ...] = Field(default_factory=tuple, description="Set of labels or tags assigned.")
    extra_info: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible contextual attribute mapping metadata."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("author", mode="after")
    @classmethod
    def validate_author_non_empty(cls, v: str) -> str:
        """Validates that author string is not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("author must be a non-empty string.")
        return v

    @field_validator("created_at", "updated_at", mode="after")
    @classmethod
    def validate_utc_timezone(cls, v: datetime) -> datetime:
        """Ensures creation and update timestamps are timezone-aware UTC."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("datetime must be a timezone-aware UTC datetime.")
        return v

    @field_validator("extra_info", mode="after")
    @classmethod
    def freeze_extra_info(cls, v: Any) -> Any:
        """Enforces immutable view protection on extra_info mapping."""
        return MappingProxyType(dict(v))

    @field_serializer("extra_info")
    def serialize_extra_info(self, extra_info: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(extra_info)


class ArchitectureDecision(BaseModel):
    """Immutable representation of an Architecture Decision Record (ADR)."""

    decision_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique tracking ID of decision.")
    title: str = Field(..., min_length=1, description="Descriptive title of decision.")
    category: DecisionCategory = Field(..., description="Classification category.")
    status: DecisionStatus = Field(..., description="Status phase classification.")
    priority: DecisionPriority = Field(..., description="Priority scale classification.")
    context: str = Field(..., min_length=1, description="Context, situation, or problem statement background.")
    decision_text: str = Field(..., min_length=1, description="Specific selected solution details or resolution.")
    consequences: str = Field(..., description="Resulting trade-offs, outcomes, or impact of decision.")
    metadata: DecisionMetadata = Field(..., description="Associated metadata descriptor properties.")
    relationships: Tuple[DecisionRelationship, ...] = Field(
        default_factory=tuple, description="Set of relationship links to other decisions."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("title", "context", "decision_text", mode="after")
    @classmethod
    def validate_non_empty_strings(cls, v: str) -> str:
        """Validates that key string fields are not empty or whitespace."""
        if not v or not v.strip():
            raise ValueError("Value must be a non-empty string.")
        return v


class DecisionRequest(BaseModel):
    """Immutable DTO payload requesting architecture decision registration or verification."""

    project_id: uuid.UUID = Field(..., description="Unique tracking identifier of project scope.")
    decision: ArchitectureDecision = Field(..., description="The target ArchitectureDecision DTO.")
    correlation_id: Optional[str] = Field(default=None, description="Optional tracking identifier.")

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class DecisionResult(BaseModel):
    """Immutable DTO representing compilation output result of decision registration/analysis."""

    result_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique result run tracking ID.")
    project_id: uuid.UUID = Field(..., description="Associated project scope identifier.")
    decision: ArchitectureDecision = Field(..., description="Target analyzed ArchitectureDecision DTO.")
    status: DecisionStatus = Field(..., description="Final resolved decision status phase.")
    processed_at: datetime = Field(..., description="UTC timezone-aware timestamp when processing occurred.")
    extra_info: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible contextual attribute mapping metadata."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("processed_at", mode="after")
    @classmethod
    def validate_utc_timezone(cls, v: datetime) -> datetime:
        """Ensures processing timestamp is timezone-aware UTC."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("processed_at must be a timezone-aware UTC datetime.")
        return v

    @field_validator("extra_info", mode="after")
    @classmethod
    def freeze_extra_info(cls, v: Any) -> Any:
        """Enforces immutable view protection on extra_info mapping."""
        return MappingProxyType(dict(v))

    @field_serializer("extra_info")
    def serialize_extra_info(self, extra_info: Any) -> dict:
        """Ensures serialization compatibility with mapping proxy classes."""
        return dict(extra_info)
