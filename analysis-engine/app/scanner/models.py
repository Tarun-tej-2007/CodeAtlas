"""Scanner domain data models module.

Defines Pydantic v2 models representing file metadata, directory structure,
scan performance statistics, and overall repository scan results.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field


class Language(str, Enum):
    """Supported programming languages in the CodeAtlas Analysis Engine."""

    UNKNOWN = "unknown"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"


class DiscoveredFile(BaseModel):
    """Represents metadata for a discovered file in the repository."""

    absolute_path: Path = Field(..., description="Absolute path to the discovered file.")
    relative_path: Path = Field(..., description="Relative path relative to repository root.")
    extension: str = Field(..., description="File extension including leading dot.")
    size: int = Field(..., ge=0, description="File size in bytes.")
    language: Language = Field(default=Language.UNKNOWN, description="Detected programming language.")

    model_config = ConfigDict(frozen=True)


class DiscoveryResult(BaseModel):
    """Represents the collection of all discovered files in the workspace."""

    files: list[DiscoveredFile] = Field(default_factory=list, description="List of recursively discovered files.")

    model_config = ConfigDict(frozen=True)


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

    # Legacy fields (retained for backward compatibility)
    repository_root: Path | None = Field(default=None, description="Root directory path of the scanned repository.")
    files: list[FileMetadata] = Field(default_factory=list, description="List of scanned source file metadata.")
    directories: list[DirectoryMetadata] = Field(default_factory=list, description="List of processed directory metadata.")
    statistics: ScanStatistics = Field(default_factory=ScanStatistics, description="Summary statistics of the scan operation.")

    # New pipeline scan fields
    discovery_result: DiscoveryResult | None = Field(default=None, description="The result of the file discovery process.")
    total_files: int = Field(default=0, ge=0, description="Total number of discovered files.")
    supported_files: int = Field(default=0, ge=0, description="Number of files matching supported languages.")
    unsupported_files: int = Field(default=0, ge=0, description="Number of files with unknown/unsupported languages.")
    languages: dict[Language, int] = Field(default_factory=dict, description="Counts of files grouped by language.")
    scan_duration: float = Field(default=0.0, ge=0.0, description="Scan execution duration in seconds.")

    model_config = ConfigDict(frozen=True)
