"""Scanner domain data models module.

Defines Pydantic v2 models representing file metadata, directory structure,
scan performance statistics, and overall repository scan results.
"""

from datetime import datetime
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field


class FileMetadata(BaseModel):
    """Represents metadata for an individual file within a scanned repository."""

    path: Path = Field(..., description="Absolute filesystem path to the file.")
    relative_path: Path = Field(..., description="Path relative to the repository root.")
    filename: str = Field(..., description="Full filename including extension.")
    extension: str = Field(..., description="File extension including leading dot.")
    size_bytes: int = Field(..., ge=0, description="File size in bytes.")
    modified_at: datetime = Field(..., description="UTC timestamp of last modification.")
    language: str | None = Field(default=None, description="Detected programming language.")

    model_config = ConfigDict(frozen=True)


class DirectoryMetadata(BaseModel):
    """Represents metadata for a directory within a scanned repository."""

    path: Path = Field(..., description="Absolute filesystem path to the directory.")
    relative_path: Path = Field(..., description="Path relative to the repository root.")
    depth: int = Field(..., ge=0, description="Directory depth level relative to repository root.")

    model_config = ConfigDict(frozen=True)


class ScanStatistics(BaseModel):
    """Holds performance and counting metrics for a completed repository scan."""

    total_files: int = Field(default=0, ge=0, description="Total files encountered during traversal.")
    source_files: int = Field(default=0, ge=0, description="Source code files matching target extensions.")
    ignored_files: int = Field(default=0, ge=0, description="Files skipped due to filter/ignore rules.")
    directories: int = Field(default=0, ge=0, description="Total directories processed.")
    scan_duration_ms: float = Field(default=0.0, ge=0.0, description="Total scan execution duration in milliseconds.")


class ScanResult(BaseModel):
    """Represents the complete result of a repository scan operation."""

    repository_root: Path = Field(..., description="Root directory path of the scanned repository.")
    files: list[FileMetadata] = Field(default_factory=list, description="List of scanned source file metadata.")
    directories: list[DirectoryMetadata] = Field(default_factory=list, description="List of processed directory metadata.")
    statistics: ScanStatistics = Field(default_factory=ScanStatistics, description="Summary statistics of the scan operation.")
