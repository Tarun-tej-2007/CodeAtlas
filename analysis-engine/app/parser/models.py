"""Parser domain data models module.

Defines immutable Pydantic v2 models representing parsed file AST objects
and aggregated parse result statistics.
"""

from pathlib import Path
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.parser.language import Language


class ParsedFile(BaseModel):
    """Represents a single parsed source code file and its associated syntax tree."""

    path: Path = Field(..., description="Absolute filesystem path to the parsed file.")
    relative_path: Path = Field(..., description="Path relative to the repository root.")
    language: Language = Field(..., description="Canonical programming language of the file.")
    source_code: str = Field(..., description="Raw source code content of the file.")
    tree: Any = Field(..., description="Tree-sitter Tree object containing the AST.")

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class ParseResult(BaseModel):
    """Represents aggregate results from a repository or multi-file parsing operation."""

    files: list[ParsedFile] = Field(default_factory=list, description="List of successfully parsed file models.")
    parsed_count: int = Field(default=0, ge=0, description="Count of successfully parsed files.")
    failed_count: int = Field(default=0, ge=0, description="Count of files that failed parsing.")
    parse_duration_ms: float = Field(default=0.0, ge=0.0, description="Total parsing duration in milliseconds.")
