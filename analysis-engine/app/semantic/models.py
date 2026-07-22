"""Semantic domain data models module."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.scanner.models import Language
from app.semantic.enums import (
    SymbolKind,
    ScopeKind,
    ReferenceKind,
    VisibilityKind,
)


class Location(BaseModel):
    """Represents a coordinate range inside a source code file."""

    start_line: int = Field(..., ge=1, description="1-indexed starting line number.")
    start_column: int = Field(..., ge=0, description="0-indexed starting column offset.")
    end_line: int = Field(..., ge=1, description="1-indexed ending line number.")
    end_column: int = Field(..., ge=0, description="0-indexed ending column offset.")

    model_config = ConfigDict(frozen=True)


class SemanticSymbol(BaseModel):
    """Represents a semantic symbol declaration in the codebase."""

    id: str = Field(..., description="Deterministic unique identifier for the symbol.")
    name: str = Field(..., description="Short name identifier of the symbol.")
    qualified_name: str = Field(..., description="Fully qualified package/module path of the symbol.")
    kind: SymbolKind = Field(..., description="Semantic symbol kind classification.")
    language: Language = Field(..., description="Programming language source of the symbol.")
    file_path: Path = Field(..., description="Absolute filesystem path containing this symbol.")
    location: Location = Field(..., description="Source code coordinate location.")
    parent_symbol_id: Optional[str] = Field(default=None, description="Optional parent symbol container identifier.")
    scope_id: Optional[str] = Field(default=None, description="Scope block containing this symbol.")
    visibility: VisibilityKind = Field(default=VisibilityKind.PUBLIC, description="Symbol visibility accessibility level.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary extension metadata dictionary.")

    model_config = ConfigDict(frozen=True)


class SemanticReference(BaseModel):
    """Represents a usage or reference reference to a semantic symbol."""

    symbol_id: str = Field(..., description="Target symbol identifier being referenced.")
    reference_kind: ReferenceKind = Field(..., description="Type of reference execution (e.g. call, read).")
    location: Location = Field(..., description="Source coordinate location of the reference.")

    model_config = ConfigDict(frozen=True)


class SemanticScope(BaseModel):
    """Represents a lexical/symbolic resolution scope container."""

    id: str = Field(..., description="Unique scope block identifier.")
    kind: ScopeKind = Field(..., description="Scope categorization block kind.")
    parent_scope_id: Optional[str] = Field(default=None, description="Optional enclosing scope parent ID.")
    symbol_ids: List[str] = Field(default_factory=list, description="Collection of symbol IDs declared directly in this scope.")

    model_config = ConfigDict(frozen=True)


class SemanticResult(BaseModel):
    """Aggregated semantic output results for a codebase analysis block."""

    symbols: List[SemanticSymbol] = Field(default_factory=list, description="All declared symbols.")
    references: List[SemanticReference] = Field(default_factory=list, description="All cross-references.")
    scopes: List[SemanticScope] = Field(default_factory=list, description="All resolved lexical scopes.")
    diagnostics: List[str] = Field(default_factory=list, description="Semantic diagnostics or error warning reports.")

    model_config = ConfigDict(frozen=True)
