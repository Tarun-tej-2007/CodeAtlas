"""Module domain data models module.

Defines immutable Pydantic v2 models and enums representing import and export symbols,
import/export kinds, and aggregated ModuleMetadata.
"""

from enum import StrEnum
from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field


class ImportKind(StrEnum):
    """Supported import statement kinds."""

    DEFAULT = "default"
    NAMED = "named"
    NAMESPACE = "namespace"
    SIDE_EFFECT = "side_effect"


class ExportKind(StrEnum):
    """Supported export statement kinds."""

    DEFAULT = "default"
    NAMED = "named"
    ALL = "all"


class ImportSymbol(BaseModel):
    """Represents an individual module import declaration."""

    id: str = Field(..., description="Deterministic unique identifier for the import symbol.")
    module: str = Field(..., description="Module specifier path or package name.")
    name: str = Field(..., description="Imported identifier name (e.g. 'useState', '*', 'default').")
    alias: str | None = Field(default=None, description="Local alias for the imported symbol if renamed.")
    kind: ImportKind = Field(..., description="Kind of import statement.")
    path: Path = Field(..., description="Absolute filesystem path to the file.")
    start_line: int = Field(..., ge=1, description="1-indexed starting line number of the import statement.")

    model_config = ConfigDict(frozen=True)


class ExportSymbol(BaseModel):
    """Represents an individual module export declaration."""

    id: str = Field(..., description="Deterministic unique identifier for the export symbol.")
    name: str = Field(..., description="Exported identifier name (e.g. 'Button', 'default', '*').")
    alias: str | None = Field(default=None, description="Alias name if exported with a different name.")
    kind: ExportKind = Field(..., description="Kind of export statement.")
    path: Path = Field(..., description="Absolute filesystem path to the file.")
    start_line: int = Field(..., ge=1, description="1-indexed starting line number of the export statement.")

    model_config = ConfigDict(frozen=True)


class ModuleMetadata(BaseModel):
    """Represents aggregate import and export declarations extracted from a module document."""

    imports: list[ImportSymbol] = Field(default_factory=list, description="Ordered list of extracted import symbols.")
    exports: list[ExportSymbol] = Field(default_factory=list, description="Ordered list of extracted export symbols.")
    import_count: int = Field(default=0, ge=0, description="Total count of import symbols.")
    export_count: int = Field(default=0, ge=0, description="Total count of export symbols.")

    model_config = ConfigDict(frozen=True)
