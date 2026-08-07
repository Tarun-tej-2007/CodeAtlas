"""Defines StrEnum categories, priorities, and granularities for AI context mapping and AI reviews."""

from enum import StrEnum


class ContextType(StrEnum):
    """Represents types of codebase context blocks generated for AI prompts."""

    FILE = "file"
    SYMBOL = "symbol"
    ARCHITECTURE = "architecture"
    GRAPH = "graph"
    SEMANTIC = "semantic"


class ContextPriority(StrEnum):
    """Represents the importance level of a context section for inclusion in prompts."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class SummaryGranularity(StrEnum):
    """Represents the depth of detail of code summaries."""

    HIGH_LEVEL = "high_level"
    DETAILED = "detailed"
    COMPACT = "compact"
    RAW = "raw"


class AIAnalysisCategory(StrEnum):
    """Represents categories of AI analyses."""

    EXPLANATION = "explanation"
    REFACTORING = "refactoring"
    DEBUGGING = "debugging"
    IMPACT = "impact"


# Sprint 30 Domain Foundation additions:


class AIProvider(StrEnum):
    """Supported AI LLM platform providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"
    MOCK = "mock"


class AIAnalysisStatus(StrEnum):
    """Lifecycle execution statuses of AI intelligence analyses."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class RecommendationPriority(StrEnum):
    """Priority scale classification levels for generated AI recommendations."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class RecommendationCategory(StrEnum):
    """Categorized areas of focus for AI generated recommendations."""

    ARCHITECTURE = "architecture"
    REFACTORING = "refactoring"
    PERFORMANCE = "performance"
    SECURITY = "security"
    TESTING = "testing"
    DEPENDENCY = "dependency"
    MAINTAINABILITY = "maintainability"
    TECHNICAL_DEBT = "technical_debt"
    DOCUMENTATION = "documentation"


class AIAnalysisType(StrEnum):
    """Supported analysis task types executed by the AI service engine."""

    FULL_ARCHITECTURE_REVIEW = "full_architecture_review"
    REFACTORING_REVIEW = "refactoring_review"
    SECURITY_REVIEW = "security_review"
    PERFORMANCE_REVIEW = "performance_review"
    TECHNICAL_DEBT_REVIEW = "technical_debt_review"
    GOVERNANCE_REVIEW = "governance_review"
    ADR_REVIEW = "adr_review"
    CUSTOM = "custom"
