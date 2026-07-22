"""Analysis engine schema definitions for the CodeAtlas Server."""

from enum import Enum
from typing import Any
import uuid
from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    """Enumeration of possible analysis job statuses."""

    ACCEPTED = "accepted"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisRequest(BaseModel):
    """Schema representing an incoming repository analysis request."""

    repository_url: str = Field(..., description="Git clone URL of the repository to analyze.")
    project_id: uuid.UUID = Field(..., description="Unique ID of the project workspace.")


class AnalysisResponse(BaseModel):
    """Schema representing the status response of a repository analysis request."""

    job_id: uuid.UUID = Field(..., description="Unique tracking ID of the analysis job.")
    status: AnalysisStatus = Field(..., description="Current status of the analysis task.")
    message: str = Field(..., description="User-friendly status message.")
    project_id: uuid.UUID = Field(..., description="Unique ID of the project workspace.")
    repository_url: str = Field(..., description="Git clone URL of the repository.")


class ErrorDetails(BaseModel):
    """Details describing a specific API error."""

    code: str = Field(..., description="Machine-readable error code.")
    message: str = Field(..., description="Human-readable descriptive message.")
    details: Any = Field(default=None, description="Optional supporting error details.")


class StandardErrorResponse(BaseModel):
    """Standardized top-level API error wrapper schema."""

    error: ErrorDetails
