"""Dashboard Domain Models Module."""

import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping
from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.dashboard.enums import DashboardStatus, DashboardWidgetType


class DashboardMetadata(BaseModel):
    """Immutable metadata tracking dashboard status and workspace properties."""

    project_name: str = Field(..., min_length=1, description="Name of the associated analyzed codebase project.")
    created_at: datetime = Field(..., description="UTC timezone-aware dashboard creation timestamp.")
    status: DashboardStatus = Field(..., description="Current status of the dashboard state.")
    extra_info: Mapping[str, Any] = Field(
        default_factory=dict, description="Custom extensible metadata fields."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("project_name", mode="after")
    @classmethod
    def validate_non_empty_project_name(cls, v: str) -> str:
        """Asserts project_name is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("project_name must not be empty or whitespace-only.")
        return v

    @field_validator("created_at", mode="after")
    @classmethod
    def validate_utc_timestamp(cls, v: datetime) -> datetime:
        """Ensures created_at timestamp is timezone-aware and set to UTC timezone."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("created_at must be a timezone-aware UTC datetime.")
        return v

    @field_validator("extra_info", mode="after")
    @classmethod
    def freeze_extra_info(cls, v: Any) -> Any:
        """Enforces immutable mapping view on extra_info dictionary."""
        return MappingProxyType(dict(v))


class DashboardWidget(BaseModel):
    """Immutable single component card widget rendering metrics details."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique identifier for the widget.")
    type: DashboardWidgetType = Field(..., description="Widget rendering and layout display type.")
    title: str = Field(..., min_length=1, description="Display header for the widget card.")
    content: Any = Field(..., description="Arbitrary content details associated with this widget.")
    metadata: Mapping[str, Any] = Field(
        default_factory=dict, description="Additional custom widget metadata details."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("title", mode="after")
    @classmethod
    def validate_non_empty_title(cls, v: str) -> str:
        """Asserts widget title is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("title must not be empty or whitespace-only.")
        return v

    @field_validator("metadata", mode="after")
    @classmethod
    def freeze_metadata(cls, v: Any) -> Any:
        """Enforces immutable mapping view on metadata dictionary."""
        return MappingProxyType(dict(v))


class DashboardModel(BaseModel):
    """Immutable aggregate domain root model representing the complete Dashboard state."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique tracking identifier for this dashboard.")
    metadata: DashboardMetadata = Field(..., description="Metadata detailing dashboard states.")
    widgets: Mapping[str, DashboardWidget] = Field(
        default_factory=dict, description="Widgets mapping index containers."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("widgets", mode="after")
    @classmethod
    def freeze_widgets(cls, v: Any) -> Any:
        """Enforces immutable mapping view on widgets dictionary."""
        return MappingProxyType(dict(v))
