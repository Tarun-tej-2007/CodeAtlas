"""Static analysis domain data models module.

Defines immutable Pydantic v2 models for AnalysisContext, Diagnostics, Severity,
and AnalysisResult objects.
"""

from enum import StrEnum
from pathlib import Path
from typing import Any
from pydantic import BaseModel, ConfigDict, Field

from app.parser.ast import ASTDocument
from app.parser.modules import ModuleMetadata
from app.parser.symbols import SymbolTable


class Severity(StrEnum):
    """Diagnostic severity levels."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Diagnostic(BaseModel):
    """Represents a diagnostic issue or insight emitted by a static analyzer."""

    id: str = Field(..., description="Deterministic unique identifier for the diagnostic.")
    severity: Severity = Field(..., description="Severity level of the diagnostic.")
    message: str = Field(..., description="Human-readable description message.")
    path: Path = Field(..., description="Absolute filesystem path to the file.")
    line: int = Field(..., ge=1, description="1-indexed line number where the issue occurs.")

    model_config = ConfigDict(frozen=True)


class AnalysisContext(BaseModel):
    """Encapsulates semantic models for a single file context passed to static analyzers."""

    ast_document: ASTDocument = Field(..., description="Normalized ASTDocument model.")
    symbol_table: SymbolTable = Field(..., description="Extracted SymbolTable model.")
    module_metadata: ModuleMetadata = Field(..., description="Extracted ModuleMetadata model.")

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class AnalysisResult(BaseModel):
    """Represents aggregated results from static analysis execution."""

    diagnostics: list[Diagnostic] = Field(default_factory=list, description="List of emitted diagnostics.")
    metrics: dict[str, Any] = Field(default_factory=dict, description="Summary metrics and analytics dictionary.")
    duration_ms: float = Field(default=0.0, ge=0.0, description="Total analysis pipeline duration in milliseconds.")

    model_config = ConfigDict(frozen=True)
