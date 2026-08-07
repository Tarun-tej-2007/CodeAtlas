"""AI Context and Analysis Pydantic v2 Models module."""

import uuid
from datetime import datetime, timezone
from types import MappingProxyType
from typing import Any, Dict, List, Mapping, Optional, Tuple

from pydantic import BaseModel, ConfigDict, Field, field_serializer, field_validator

from app.ai.enums import (
    AIAnalysisStatus,
    AIAnalysisType,
    AIProvider,
    ContextPriority,
    ContextType,
    RecommendationCategory,
    RecommendationPriority,
    SummaryGranularity,
)


def _validate_utc_time(v: datetime) -> datetime:
    """Helper to validate that a datetime is UTC timezone aware."""
    if v.tzinfo is None or v.tzinfo != timezone.utc:
        raise ValueError("Timestamp must be a timezone-aware UTC datetime.")
    return v


def _validate_non_empty_str(v: str) -> str:
    """Helper to validate that string is not empty or whitespace."""
    if not v or not v.strip():
        raise ValueError("String field must be non-empty.")
    return v.strip()


# Original AI Context Builder models:


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


# New Sprint 30 AI Architecture Intelligence domain models:


class AIMetadata(BaseModel):
    """Immutable model representing setup properties configuration for an AI query session."""

    author: str = Field(..., description="Requesting author handle.")
    created_at: datetime = Field(..., description="UTC timezone-aware timestamp when metadata was created.")
    provider: AIProvider = Field(..., description="Target AI LLM provider platform.")
    model_name: str = Field(..., description="Specific LLM model identifier string.")
    temperature: float = Field(default=0.0, ge=0.0, le=2.0, description="Sampling temperature limit.")
    extra_info: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible contextual metadata attributes map."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("created_at")
    @classmethod
    def validate_created_at_utc(cls, v: datetime) -> datetime:
        return _validate_utc_time(v)

    @field_validator("author", "model_name")
    @classmethod
    def validate_strings(cls, v: str) -> str:
        return _validate_non_empty_str(v)

    @field_validator("extra_info")
    @classmethod
    def freeze_extra_info(cls, v: Any) -> Any:
        return MappingProxyType(dict(v))

    @field_serializer("extra_info")
    def serialize_extra_info(self, extra_info: Any) -> dict:
        return dict(extra_info)


class AIRequest(BaseModel):
    """Immutable model representing a request configuration payload for executing an AI analysis run."""

    project_id: uuid.UUID = Field(..., description="Associated project unique tracking identifier.")
    commit_id: str = Field(..., description="Target Git commit hash.")
    analysis_type: AIAnalysisType = Field(..., description="Target analysis task type classification.")
    metadata: AIMetadata = Field(..., description="AI query session metadata properties.")
    custom_instructions: Optional[str] = Field(default=None, description="Optional custom user prompts instructions.")

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("commit_id")
    @classmethod
    def validate_commit_id(cls, v: str) -> str:
        return _validate_non_empty_str(v)


class AIContext(BaseModel):
    """Immutable model collecting structured repository artifacts context feeding to prompt builders."""

    project_id: uuid.UUID = Field(..., description="Associated project UUID.")
    commit_id: str = Field(..., description="Associated Git commit hash.")
    dependency_graph_summary: Optional[str] = Field(default=None, description="Summarized dependency graph mappings.")
    architecture_issues: Tuple[str, ...] = Field(default_factory=tuple, description="Discovered architecture issues.")
    governance_violations: Tuple[str, ...] = Field(default_factory=tuple, description="Active rule violation summaries.")
    decisions_summary: Tuple[str, ...] = Field(default_factory=tuple, description="Historical decisions context summary.")
    files_count: int = Field(default=0, ge=0, description="Total number of analyzed files in scope.")
    extra_context: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible contextual metadata helper maps."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("commit_id")
    @classmethod
    def validate_commit_id(cls, v: str) -> str:
        return _validate_non_empty_str(v)

    @field_validator("extra_context")
    @classmethod
    def freeze_extra_context(cls, v: Any) -> Any:
        return MappingProxyType(dict(v))

    @field_serializer("extra_context")
    def serialize_extra_context(self, extra_context: Any) -> dict:
        return dict(extra_context)


class PromptContext(BaseModel):
    """Immutable model holding interpolated prompts inputs passed down to LLM providers."""

    system_prompt: str = Field(..., description="System context instructions prompt.")
    user_prompt: str = Field(..., description="User query prompt input.")
    variables: Mapping[str, Any] = Field(
        default_factory=dict, description="Variables list dict parsed by template engines."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("system_prompt", "user_prompt")
    @classmethod
    def validate_prompts(cls, v: str) -> str:
        return _validate_non_empty_str(v)

    @field_validator("variables")
    @classmethod
    def freeze_variables(cls, v: Any) -> Any:
        return MappingProxyType(dict(v))

    @field_serializer("variables")
    def serialize_variables(self, variables: Any) -> dict:
        return dict(variables)


class AIRecommendation(BaseModel):
    """Immutable recommendation model capturing actionable fix items produced by AI services."""

    recommendation_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique recommendation ID.")
    title: str = Field(..., description="Actionable title description.")
    description: str = Field(..., description="Detailed review finding description.")
    category: RecommendationCategory = Field(..., description="Focused target category.")
    priority: RecommendationPriority = Field(..., description="Associated classification priority.")
    affected_files: Tuple[str, ...] = Field(default_factory=tuple, description="Set of target files affected.")
    suggested_fix: Optional[str] = Field(default=None, description="Remediation code snippet or suggestion.")
    remediation_effort: Optional[str] = Field(default=None, description="Optional description of estimated workload.")

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("title", "description")
    @classmethod
    def validate_strings(cls, v: str) -> str:
        return _validate_non_empty_str(v)


class AIUsageStatistics(BaseModel):
    """Immutable statistics tracking token consumption metrics across API requests."""

    prompt_tokens: int = Field(default=0, ge=0, description="Input query prompt tokens consumed.")
    completion_tokens: int = Field(default=0, ge=0, description="Output response completion tokens consumed.")
    total_tokens: int = Field(default=0, ge=0, description="Aggregated total token consumption.")
    estimated_cost: Optional[float] = Field(default=None, ge=0.0, description="Estimated total run cost in USD.")

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)


class AIAnalysis(BaseModel):
    """Immutable model representing an active or finished AI review pipeline run instance."""

    analysis_id: uuid.UUID = Field(default_factory=uuid.uuid4, description="Unique analysis execution ID.")
    project_id: uuid.UUID = Field(..., description="Associated project Scope identifier UUID.")
    commit_id: str = Field(..., description="Associated target commit hash.")
    analysis_type: AIAnalysisType = Field(..., description="Associated analysis run type category.")
    status: AIAnalysisStatus = Field(..., description="Current running status phase lifecycle.")
    recommendations: Tuple[AIRecommendation, ...] = Field(
        default_factory=tuple, description="Collection of actionable recommendation outputs."
    )
    statistics: AIUsageStatistics = Field(
        default_factory=AIUsageStatistics, description="Associated LLM token usage stats tracking."
    )
    started_at: datetime = Field(..., description="UTC timezone-aware timestamp when run initialized.")
    completed_at: Optional[datetime] = Field(default=None, description="UTC timezone-aware timestamp when run finished.")
    error_message: Optional[str] = Field(default=None, description="Error message if status is FAILED.")

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("commit_id")
    @classmethod
    def validate_commit_id(cls, v: str) -> str:
        return _validate_non_empty_str(v)

    @field_validator("started_at")
    @classmethod
    def validate_started_at(cls, v: datetime) -> datetime:
        return _validate_utc_time(v)

    @field_validator("completed_at")
    @classmethod
    def validate_completed_at(cls, v: Optional[datetime]) -> Optional[datetime]:
        if v is not None:
            return _validate_utc_time(v)
        return v


class AIResult(BaseModel):
    """Immutable result wrapper containing compiled AIAnalysis output details."""

    project_id: uuid.UUID = Field(..., description="Associated project scoping ID.")
    commit_id: str = Field(..., description="Associated Git commit hash.")
    analysis: AIAnalysis = Field(..., description="Compiled AIAnalysis instance details.")
    extra_info: Mapping[str, Any] = Field(
        default_factory=dict, description="Extensible contextual tracking attributes mapping."
    )

    model_config = ConfigDict(frozen=True, arbitrary_types_allowed=True)

    @field_validator("commit_id")
    @classmethod
    def validate_commit_id(cls, v: str) -> str:
        return _validate_non_empty_str(v)

    @field_validator("extra_info")
    @classmethod
    def freeze_extra_info(cls, v: Any) -> Any:
        return MappingProxyType(dict(v))

    @field_serializer("extra_info")
    def serialize_extra_info(self, extra_info: Any) -> dict:
        return dict(extra_info)
