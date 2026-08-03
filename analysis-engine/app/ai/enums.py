"""AI Context Domain Enums module.

Defines StrEnum categories, priorities, and granularities for AI context mapping.
"""

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
