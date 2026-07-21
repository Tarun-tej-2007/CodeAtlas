"""Symbol resolution domain data models module.

Defines immutable Pydantic v2 models representing resolved identifier references
and aggregated ResolutionResult objects.
"""

from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field


class ResolvedReference(BaseModel):
    """Represents an identifier reference resolved against in-file symbol declarations."""

    id: str = Field(..., description="Deterministic unique identifier for the reference.")
    name: str = Field(..., description="Identifier name being referenced.")
    path: Path = Field(..., description="Absolute filesystem path to the file.")
    line: int = Field(..., ge=1, description="1-indexed line number of the identifier usage.")
    column: int = Field(..., ge=0, description="0-indexed column offset of the identifier usage.")
    resolved_symbol_id: str | None = Field(default=None, description="ID of resolved declaration Symbol, if found.")
    resolved: bool = Field(..., description="True if symbol declaration was found in scope, False otherwise.")

    model_config = ConfigDict(frozen=True)


class ResolutionResult(BaseModel):
    """Represents aggregated results from intra-file symbol resolution."""

    references: list[ResolvedReference] = Field(default_factory=list, description="Ordered list of identifier references.")
    resolved_count: int = Field(default=0, ge=0, description="Count of successfully resolved references.")
    unresolved_count: int = Field(default=0, ge=0, description="Count of unresolved references.")

    model_config = ConfigDict(frozen=True)
