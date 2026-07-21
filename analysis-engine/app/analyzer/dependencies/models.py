"""Dependency domain data models module.

Defines immutable Pydantic v2 models representing intra-file symbol dependencies,
module-level import/export dependencies, and aggregated DependencyResult objects.
"""

from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field


class DependencyKind(StrEnum):
    """Supported dependency relationship kinds."""

    CALL = "call"
    IMPORT = "import"
    EXPORT = "export"
    REFERENCE = "reference"


class Dependency(BaseModel):
    """Represents a symbol-level dependency relationship (e.g. function call or variable reference)."""

    id: str = Field(..., description="Deterministic unique identifier for the dependency.")
    source_id: str = Field(..., description="ID of source symbol or file path string.")
    target_id: str | None = Field(default=None, description="ID of target symbol or callee name if unresolved.")
    kind: DependencyKind = Field(..., description="Kind of dependency relationship.")
    path: Path = Field(..., description="Absolute filesystem path to the file.")
    line: int = Field(..., ge=1, description="1-indexed line number of the dependency relationship.")
    resolved: bool = Field(..., description="True if target symbol was resolved, False otherwise.")

    model_config = ConfigDict(frozen=True)


class ModuleDependency(BaseModel):
    """Represents a module-level import or export dependency relationship."""

    id: str = Field(..., description="Deterministic unique identifier for the module dependency.")
    source_module: str = Field(..., description="Source module path string or file path.")
    target_module: str = Field(..., description="Target module specifier string (e.g. './utils', 'react').")
    kind: DependencyKind = Field(..., description="Kind of module dependency (IMPORT or EXPORT).")

    model_config = ConfigDict(frozen=True)


class DependencyResult(BaseModel):
    """Represents aggregated results from dependency relationship building."""

    dependencies: list[Dependency] = Field(default_factory=list, description="Ordered list of symbol-level dependencies.")
    module_dependencies: list[ModuleDependency] = Field(default_factory=list, description="Ordered list of module-level dependencies.")
    dependency_count: int = Field(default=0, ge=0, description="Total count of symbol dependencies.")
    resolved_count: int = Field(default=0, ge=0, description="Count of resolved symbol dependencies.")
    unresolved_count: int = Field(default=0, ge=0, description="Count of unresolved symbol dependencies.")

    model_config = ConfigDict(frozen=True)
