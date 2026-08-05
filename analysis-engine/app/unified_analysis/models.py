"""Unified Analysis Domain Models Module."""

from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Optional
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.unified_analysis.enums import AnalysisStatus


class UnifiedAnalysisReport(BaseModel):
    """Immutable aggregate model representing complete codebase analysis output collections."""

    project_name: str = Field(..., min_length=1, description="Analyzed project name.")
    generated_at: datetime = Field(..., description="Timezone-aware UTC execution timestamp.")
    status: AnalysisStatus = Field(default=AnalysisStatus.SUCCESS, description="Unified execution status.")

    scan_result: Optional[Any] = Field(default=None, description="Optional scan result structure.")
    parse_result: Optional[Any] = Field(default=None, description="Optional parser output structure.")
    architecture_result: Optional[Any] = Field(default=None, description="Optional architecture analysis output structure.")
    quality_result: Optional[Any] = Field(default=None, description="Optional code quality analysis output structure.")
    technical_debt_result: Optional[Any] = Field(default=None, description="Optional technical debt analysis output structure.")

    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible execution settings and metadata details."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

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
        """Enforces read-only dictionary views on metadata at runtime."""
        return MappingProxyType(dict(v))
