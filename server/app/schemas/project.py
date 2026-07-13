import uuid
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, ConfigDict
from app.models.enums import ProjectVisibility

class ProjectCreate(BaseModel):
    """
    Schema for validating project creation requests.
    """
    name: str = Field(..., max_length=150, description="The name of the project.")
    description: str | None = Field(default=None, max_length=500, description="Optional project description.")
    visibility: ProjectVisibility = Field(default=ProjectVisibility.PRIVATE, description="Project visibility.")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        trimmed = v.strip() if v else ""
        if not trimmed:
            raise ValueError("Project name must not be empty or whitespace only")
        return trimmed

class ProjectUpdate(BaseModel):
    """
    Schema for validating project update requests.
    Supports partial updates.
    """
    name: str | None = Field(default=None, max_length=150, description="The updated name of the project.")
    description: str | None = Field(default=None, max_length=500, description="The updated project description.")
    visibility: ProjectVisibility | None = Field(default=None, description="The updated project visibility.")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        if v is not None:
            trimmed = v.strip()
            if not trimmed:
                raise ValueError("Project name must not be empty or whitespace only")
            return trimmed
        return v

class ProjectResponse(BaseModel):
    """
    Schema representing a project serialization format returned by APIs.
    """
    id: uuid.UUID
    owner_id: uuid.UUID
    name: str
    slug: str
    description: str | None
    visibility: ProjectVisibility
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
