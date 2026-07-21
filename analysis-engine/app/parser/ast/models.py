"""Normalized AST domain models module.

Defines immutable Pydantic v2 models representing language-agnostic AST nodes
and document hierarchies.
"""

from pathlib import Path
from pydantic import BaseModel, ConfigDict, Field

from app.parser.language import Language


class ASTNode(BaseModel):
    """Represents a single node within the normalized CodeAtlas AST hierarchy."""

    id: str = Field(..., description="Deterministic unique identifier for the AST node.")
    type: str = Field(..., description="Syntax type of the node (e.g. 'program', 'identifier').")
    text: str = Field(..., description="Source code text snippet corresponding to the node.")
    start_line: int = Field(..., ge=1, description="1-indexed starting line number in source code.")
    start_column: int = Field(..., ge=0, description="0-indexed starting column offset.")
    end_line: int = Field(..., ge=1, description="1-indexed ending line number in source code.")
    end_column: int = Field(..., ge=0, description="0-indexed ending column offset.")
    children: list["ASTNode"] = Field(default_factory=list, description="Ordered list of child AST nodes.")

    model_config = ConfigDict(frozen=True)


class ASTDocument(BaseModel):
    """Represents a complete normalized AST document for a single source file."""

    path: Path = Field(..., description="Absolute filesystem path to the source file.")
    relative_path: Path = Field(..., description="Path relative to the repository root.")
    language: Language = Field(..., description="Canonical language enum of the file.")
    root: ASTNode = Field(..., description="Root ASTNode of the document hierarchy.")

    model_config = ConfigDict(frozen=True)
