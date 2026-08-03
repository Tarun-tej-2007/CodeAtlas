"""AI Context Domain Models module.

Defines immutable Pydantic v2 models representing structured sections,
symbols, repository metrics, and context payloads for AI reasoning.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.ai.enums import ContextPriority, ContextType, SummaryGranularity


class ContextSection(BaseModel):
    """Represents a discrete section of codebase context (e.g. file content, class details)."""

    id: str = Field(..., description="Unique stable identifier for this section.")
    title: str = Field(..., description="Human-readable title of the section.")
    content: str = Field(..., description="Text content containing source, docstrings, or description.")
    priority: ContextPriority = Field(
        default=ContextPriority.MEDIUM, description="Priority weight of this context block."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Extensible metadata attributes."
    )

    model_config = ConfigDict(frozen=True)


class SymbolContext(BaseModel):
    """Represents isolated symbol boundary details including dependencies and dependents."""

    symbol_id: str = Field(..., description="The unique symbol identifier.")
    qualified_name: str = Field(..., description="Qualified dot-path identifier of the symbol.")
    kind: str = Field(..., description="The kind classification of the symbol (e.g. 'function').")
    definition_summary: str = Field(..., description="Textual summary of the symbol definition signature.")
    dependencies: List[str] = Field(
        default_factory=list, description="IDs of other symbols this symbol depends on."
    )
    dependents: List[str] = Field(
        default_factory=list, description="IDs of other symbols that depend on this symbol."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Custom symbol context properties."
    )

    model_config = ConfigDict(frozen=True)


class RepositoryContext(BaseModel):
    """Represents high-level metrics and identifiers of the scanned repository workspace."""

    repo_name: str = Field(..., description="The workspace repository name.")
    description: Optional[str] = Field(None, description="Optional brief project description.")
    file_paths: List[str] = Field(
        default_factory=list, description="List of all relative paths included in context."
    )
    primary_languages: List[str] = Field(
        default_factory=list, description="List of primary programming languages discovered."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Project-level setting values."
    )

    model_config = ConfigDict(frozen=True)


class AIContextResult(BaseModel):
    """Result payload containing the complete context package constructed for AI consumption."""

    id: str = Field(..., description="Unique stable identifier of this generation run.")
    context_type: ContextType = Field(..., description="Context type classification.")
    granularity: SummaryGranularity = Field(
        default=SummaryGranularity.COMPACT, description="Detail level of code summaries."
    )
    sections: List[ContextSection] = Field(
        default_factory=list, description="Collection of context content blocks."
    )
    symbols: List[SymbolContext] = Field(
        default_factory=list, description="Collection of symbol relational contexts."
    )
    repository: Optional[RepositoryContext] = Field(
        None, description="Workspace repository meta-metrics."
    )
    diagnostics: List[str] = Field(
        default_factory=list, description="Diagnostic logs describing context compilation."
    )
    metadata: Dict[str, str] = Field(
        default_factory=dict, description="Metadata tags describing generation run settings."
    )

    model_config = ConfigDict(frozen=True)
