"""Symbol domain data models module.

Defines immutable Pydantic v2 models and enums representing source code declarations,
kinds, and aggregated SymbolTable objects.
"""

from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field

from app.parser.language import Language


class SymbolKind(StrEnum):
    """Supported symbol declaration kinds."""

    FUNCTION = "function"
    CLASS = "class"
    METHOD = "method"
    VARIABLE = "variable"
    INTERFACE = "interface"
    TYPE_ALIAS = "type_alias"
    ENUM = "enum"
    NAMESPACE = "namespace"
    UNKNOWN = "unknown"


class Symbol(BaseModel):
    """Represents an individual source code declaration symbol."""

    id: str = Field(..., description="Deterministic unique identifier for the symbol.")
    name: str = Field(..., description="Identifier name of the declaration.")
    kind: SymbolKind = Field(..., description="Kind of declaration symbol.")
    language: Language = Field(..., description="Canonical language enum of the file.")
    path: Path = Field(..., description="Absolute filesystem path to the file.")
    parent_symbol_id: str | None = Field(default=None, description="Parent symbol ID (e.g. enclosing class for methods).")
    start_line: int = Field(..., ge=1, description="1-indexed starting line number of the declaration.")
    end_line: int = Field(..., ge=1, description="1-indexed ending line number of the declaration.")

    model_config = ConfigDict(frozen=True)


class SymbolTable(BaseModel):
    """Represents a collection of symbols extracted from an ASTDocument."""

    symbols: list[Symbol] = Field(default_factory=list, description="Ordered list of extracted declaration symbols.")
    count: int = Field(default=0, ge=0, description="Total count of extracted symbols.")

    model_config = ConfigDict(frozen=True)
