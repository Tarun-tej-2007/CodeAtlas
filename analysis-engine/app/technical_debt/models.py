"""Technical Debt Domain Models module."""

from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Dict, Mapping, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.technical_debt.enums import TechnicalDebtCategory, TechnicalDebtSeverity


class TechnicalDebtItem(BaseModel):
    """Immutable model representing an individual technical debt finding."""

    id: str = Field(..., min_length=1, description="Unique identifier for the item.")
    category: TechnicalDebtCategory = Field(..., description="The category grouping of this debt item.")
    severity: TechnicalDebtSeverity = Field(..., description="The severity class tier.")
    title: str = Field(..., min_length=1, description="Short title describing the finding.")
    description: str = Field(default="", description="Descriptive context explanation.")
    effort_minutes: int = Field(default=0, ge=0, description="Estimated effort in minutes required to resolve the debt.")
    location_file: Optional[str] = Field(default=None, description="Path of the affected file.")
    location_line: Optional[int] = Field(default=None, ge=1, description="Line number of the affected code scope.")
    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible metadata properties map."
    )

    model_config = ConfigDict(frozen=True)

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        """Enforces read-only dictionary views on metadata at runtime."""
        return MappingProxyType(dict(v))


class TechnicalDebtSummary(BaseModel):
    """Immutable model containing aggregate statistics and overall levels."""

    total_items: int = Field(..., ge=0, description="Total technical debt items.")
    total_effort_minutes: int = Field(..., ge=0, description="Aggregate effort in minutes to resolve all items.")
    items_by_category: Mapping[TechnicalDebtCategory, int] = Field(
        default_factory=dict, description="Segment counts of items per category."
    )
    effort_by_severity: Mapping[TechnicalDebtSeverity, int] = Field(
        default_factory=dict, description="Segment aggregate effort per severity level."
    )
    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Summary metadata fields."
    )

    model_config = ConfigDict(frozen=True)

    @field_validator("items_by_category", mode="after")
    @classmethod
    def freeze_items_by_category(cls, v: Any) -> Any:
        return MappingProxyType(dict(v))

    @field_validator("effort_by_severity", mode="after")
    @classmethod
    def freeze_effort_by_severity(cls, v: Any) -> Any:
        return MappingProxyType(dict(v))

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        return MappingProxyType(dict(v))


class TechnicalDebtReport(BaseModel):
    """Immutable model representing a complete project technical debt analysis report."""

    project_name: str = Field(..., min_length=1, description="Analyzed project name identifier.")
    generated_at: datetime = Field(..., description="Timezone-aware UTC generation timestamp.")
    items: Tuple[TechnicalDebtItem, ...] = Field(
        default_factory=tuple, description="Sorted list of findings."
    )
    summary: TechnicalDebtSummary = Field(..., description="Aggregated summary indexing overall stats.")
    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Overall configuration details."
    )

    model_config = ConfigDict(frozen=True)

    @field_validator("project_name", mode="after")
    @classmethod
    def validate_non_empty_project_name(cls, v: str) -> str:
        """Asserts that project_name is not empty or whitespace-only."""
        if not v.strip():
            raise ValueError("project_name must not be empty or whitespace-only.")
        return v

    @field_validator("generated_at", mode="after")
    @classmethod
    def validate_utc_timestamp(cls, v: datetime) -> datetime:
        """Asserts that the timestamp is timezone-aware and set to UTC timezone."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("generated_at must be a timezone-aware UTC datetime.")
        return v

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        return MappingProxyType(dict(v))
