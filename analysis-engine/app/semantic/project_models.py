"""Project-level semantic domain models module."""

from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.semantic.enums import SymbolKind, VisibilityKind
from app.semantic.models import Location, SemanticReference


class SymbolLocation(BaseModel):
    """Represents a location of a symbol scoped to a specific project file."""

    file_path: Path = Field(..., description="Absolute or relative path to the containing file.")
    location: Location = Field(..., description="Lexical line/column coordinates in the file.")

    model_config = ConfigDict(frozen=True)


class ProjectSymbol(BaseModel):
    """Represents a semantic symbol within the context of a project structure."""

    id: str = Field(..., description="Unique deterministic identifier for the symbol.")
    name: str = Field(..., description="Name identifier of the symbol.")
    qualified_name: str = Field(..., description="Fully qualified project-level name of the symbol.")
    kind: SymbolKind = Field(..., description="Semantic kind of the symbol.")
    location: SymbolLocation = Field(..., description="The physical file location of the symbol.")
    parent_symbol_id: Optional[str] = Field(default=None, description="Optional parent symbol reference identifier.")
    visibility: VisibilityKind = Field(default=VisibilityKind.PUBLIC, description="Symbol visibility accessibility level.")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Extensible metadata mapping dictionary.")

    model_config = ConfigDict(frozen=True)


class ImportDeclaration(BaseModel):
    """Represents an explicit import statement declaration in a source file."""

    imported_name: str = Field(..., description="The name of the symbol being imported (e.g. 'foo' or '*').")
    module_specifier: str = Field(..., description="The specifier path of the module being imported from.")
    local_alias: Optional[str] = Field(default=None, description="Optional alias alias name assigned locally.")
    location: SymbolLocation = Field(..., description="Coordinate range location of the import statement.")

    model_config = ConfigDict(frozen=True)


class ExportDeclaration(BaseModel):
    """Represents an explicit export statement declaration in a source file."""

    exported_name: str = Field(..., description="The name of the symbol being exported.")
    local_symbol_id: Optional[str] = Field(
        default=None, description="Optional ID link to a ProjectSymbol defined locally."
    )
    location: SymbolLocation = Field(..., description="Coordinate range location of the export statement.")

    model_config = ConfigDict(frozen=True)


class ProjectFile(BaseModel):
    """Represents the compiled semantic declarations and imports for a single file."""

    path: Path = Field(..., description="Absolute path to the project file.")
    symbols: List[ProjectSymbol] = Field(default_factory=list, description="All declared symbols in the file.")
    imports: List[ImportDeclaration] = Field(default_factory=list, description="All import statements in the file.")
    exports: List[ExportDeclaration] = Field(default_factory=list, description="All export statements in the file.")

    model_config = ConfigDict(frozen=True)


class ProjectSemanticResult(BaseModel):
    """Aggregated semantic output results for an entire project analysis run."""

    files: Dict[Path, ProjectFile] = Field(
        default_factory=dict, description="Mapping of project file paths to ProjectFile structures."
    )
    cross_file_references: List[SemanticReference] = Field(
        default_factory=list, description="All resolved cross-file references."
    )
    diagnostics: List[str] = Field(
        default_factory=list, description="Project-wide diagnostics or warning warnings."
    )

    model_config = ConfigDict(frozen=True)
