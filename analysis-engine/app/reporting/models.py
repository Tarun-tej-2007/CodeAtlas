"""Report Domain Models Module."""

import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.reporting.enums import ReportFormat, ReportSection


class ReportSectionContent(BaseModel):
    """Immutable section content within a report."""

    section: ReportSection = Field(..., description="The category type of this section.")
    title: str = Field(..., min_length=1, description="Descriptive section header title.")
    content: str = Field(..., description="Text content body of the section.")
    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Metadata key-value details for this section."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("title", mode="after")
    @classmethod
    def validate_non_empty_title(cls, v: str) -> str:
        """Asserts title is not empty or whitespace-only."""
        if not v.strip():
            raise ValueError("title must not be empty or whitespace-only.")
        return v

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        """Enforces immutable mapping view on metadata dictionary details."""
        return MappingProxyType(dict(v))


class ReportMetadata(BaseModel):
    """Immutable metadata tracking project identifiers, timestamps, and formats."""

    project_name: str = Field(..., min_length=1, description="Name of the analyzed codebase project.")
    generated_at: datetime = Field(..., description="UTC timezone-aware generation timestamp.")
    format: ReportFormat = Field(..., description="Target output layout format.")
    extra_info: Mapping[str, Any] = Field(
        default_factory=dict, description="Custom extensible metadata fields."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("project_name", mode="after")
    @classmethod
    def validate_non_empty_project_name(cls, v: str) -> str:
        """Asserts project_name is not empty or whitespace-only."""
        if not v.strip():
            raise ValueError("project_name must not be empty or whitespace-only.")
        return v

    @field_validator("generated_at", mode="after")
    @classmethod
    def validate_utc_timestamp(cls, v: datetime) -> datetime:
        """Ensures generated_at timestamp is timezone-aware and set to UTC timezone."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("generated_at must be a timezone-aware UTC datetime.")
        return v

    @field_validator("extra_info", mode="after")
    @classmethod
    def freeze_extra_info(cls, v: Any) -> Any:
        """Enforces immutable mapping view on extra_info dictionary details."""
        return MappingProxyType(dict(v))


class AnalysisReport(BaseModel):
    """Immutable aggregate model containing report metadata and section mappings."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique tracking identifier for this report.")
    metadata: ReportMetadata = Field(..., description="Metadata container detailing compilation parameters.")
    sections: Mapping[ReportSection, ReportSectionContent] = Field(
        ..., description="Sections index content dictionary mapping."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("sections", mode="after")
    @classmethod
    def freeze_sections(cls, v: Any) -> Any:
        """Enforces immutable mapping view on sections dictionary."""
        return MappingProxyType(dict(v))
