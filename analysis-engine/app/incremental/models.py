"""Incremental Analysis Domain Models Module."""

import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple
from pydantic import BaseModel, ConfigDict, Field, field_validator, field_serializer

from app.incremental.enums import ChangeType, IncrementalStatus


class FileFingerprint(BaseModel):
    """Immutable domain representation of a single file's fingerprint identifier and attributes."""

    path: str = Field(..., min_length=1, description="Relative file path within the project workspace.")
    hash: str = Field(..., min_length=1, description="Cryptographic hash (e.g. SHA-256) of the file content.")
    size: int = Field(..., ge=0, description="Size of the file in bytes.")
    last_modified: datetime = Field(..., description="UTC timezone-aware last modification timestamp.")

    model_config = ConfigDict(frozen=True)

    @field_validator("path", mode="after")
    @classmethod
    def validate_non_empty_path(cls, v: str) -> str:
        """Asserts path is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("File path must not be empty or whitespace-only.")
        return v

    @field_validator("hash", mode="after")
    @classmethod
    def validate_non_empty_hash(cls, v: str) -> str:
        """Asserts hash is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("File hash must not be empty or whitespace-only.")
        return v

    @field_validator("last_modified", mode="after")
    @classmethod
    def validate_utc_timestamp(cls, v: datetime) -> datetime:
        """Ensures last_modified timestamp is timezone-aware and set to UTC timezone."""
        if v.tzinfo is None or v.tzinfo != timezone.utc:
            raise ValueError("last_modified must be a timezone-aware UTC datetime.")
        return v


class RepositorySnapshot(BaseModel):
    """Immutable repository snapshot mapping file paths to their fingerprints at a specific commit."""

    commit_id: str = Field(..., min_length=1, description="Repository commit identifier hash (e.g. Git SHA-1).")
    fingerprints: Mapping[str, FileFingerprint] = Field(
        default_factory=dict, description="Mapped file fingerprints indexed by relative file path."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("commit_id", mode="after")
    @classmethod
    def validate_commit_id(cls, v: str) -> str:
        """Asserts commit_id is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("commit_id must not be empty or whitespace-only.")
        return v

    @field_validator("fingerprints", mode="after")
    @classmethod
    def freeze_fingerprints(cls, v: Any) -> Any:
        """Enforces immutable mapping view on fingerprints dictionary."""
        return MappingProxyType(dict(v))

    @field_serializer("fingerprints")
    def serialize_fingerprints(self, fingerprints: Any) -> dict:
        """Serializes mapping proxy to standard dict for Pydantic/FastAPI export."""
        return dict(fingerprints)


class ChangedFile(BaseModel):
    """Immutable domain representation detailing a single file change between snapshot points."""

    path: str = Field(..., min_length=1, description="Relative file path within the project workspace.")
    change_type: ChangeType = Field(..., description="The type of change detected (e.g. Added, Modified, Deleted).")
    old_fingerprint: Optional[FileFingerprint] = Field(
        default=None, description="Pre-change fingerprint state. Required for MODIFIED/DELETED."
    )
    new_fingerprint: Optional[FileFingerprint] = Field(
        default=None, description="Post-change fingerprint state. Required for ADDED/MODIFIED."
    )

    model_config = ConfigDict(frozen=True)

    @field_validator("path", mode="after")
    @classmethod
    def validate_non_empty_path(cls, v: str) -> str:
        """Asserts path is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("File path must not be empty or whitespace-only.")
        return v


class IncrementalAnalysisMetadata(BaseModel):
    """Immutable metadata tracking the source commits and execution status of an incremental run."""

    project_name: str = Field(..., min_length=1, description="Name of the associated analyzed codebase project.")
    source_commit: str = Field(..., min_length=1, description="Source/base commit identifier hash.")
    target_commit: str = Field(..., min_length=1, description="Target/comparison commit identifier hash.")
    created_at: datetime = Field(..., description="UTC timezone-aware dashboard creation timestamp.")
    status: IncrementalStatus = Field(..., description="Current status of the incremental state.")
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

    @field_validator("source_commit", mode="after")
    @classmethod
    def validate_source_commit(cls, v: str) -> str:
        """Asserts source_commit is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("source_commit must not be empty or whitespace-only.")
        return v

    @field_validator("target_commit", mode="after")
    @classmethod
    def validate_target_commit(cls, v: str) -> str:
        """Asserts target_commit is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("target_commit must not be empty or whitespace-only.")
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

    @field_serializer("extra_info")
    def serialize_extra_info(self, extra_info: Any) -> dict:
        """Serializes mapping proxy to standard dict for Pydantic/FastAPI export."""
        return dict(extra_info)


class IncrementalAnalysisRequest(BaseModel):
    """Immutable parameter DTO requesting incremental analysis computation."""

    project_id: uuid.UUID = Field(..., description="Unique ID of the project workspace.")
    project_name: str = Field(..., min_length=1, description="Name of the associated project.")
    source_commit: str = Field(..., min_length=1, description="Source/base commit identifier hash.")
    target_commit: str = Field(..., min_length=1, description="Target/comparison commit identifier hash.")
    changed_files: Tuple[ChangedFile, ...] = Field(
        default_factory=tuple, description="Set of file change descriptors."
    )

    model_config = ConfigDict(frozen=True)

    @field_validator("project_name", mode="after")
    @classmethod
    def validate_non_empty_project_name(cls, v: str) -> str:
        """Asserts project_name is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("project_name must not be empty or whitespace-only.")
        return v

    @field_validator("source_commit", mode="after")
    @classmethod
    def validate_source_commit(cls, v: str) -> str:
        """Asserts source_commit is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("source_commit must not be empty or whitespace-only.")
        return v

    @field_validator("target_commit", mode="after")
    @classmethod
    def validate_target_commit(cls, v: str) -> str:
        """Asserts target_commit is not empty or whitespace-only."""
        if not v or not v.strip():
            raise ValueError("target_commit must not be empty or whitespace-only.")
        return v


class IncrementalAnalysisResult(BaseModel):
    """Immutable result DTO holding finalized incremental analysis execution details."""

    analysis_id: uuid.UUID = Field(
        default_factory=uuid.uuid4, description="Unique identifier tracking this incremental run."
    )
    metadata: IncrementalAnalysisMetadata = Field(..., description="Job execution and source metadata details.")
    added_count: int = Field(default=0, ge=0, description="Total files added.")
    modified_count: int = Field(default=0, ge=0, description="Total files modified.")
    deleted_count: int = Field(default=0, ge=0, description="Total files deleted.")
    unchanged_count: int = Field(default=0, ge=0, description="Total files unchanged.")
    changed_files: Tuple[ChangedFile, ...] = Field(
        default_factory=tuple, description="Collection of file delta differences reviewed."
    )

    model_config = ConfigDict(frozen=True)
