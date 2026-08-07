"""AI Context and Analysis package.

Establishes structural enums, custom exceptions, model definitions, and pipeline
interfaces for constructing AI context packages and executing AI reviews.
"""

# Re-export original enums
from app.ai.enums import (
    AIAnalysisCategory,
    AIAnalysisStatus,
    AIAnalysisType,
    AIProvider,
    ContextPriority,
    ContextType,
    RecommendationCategory,
    RecommendationPriority,
    SummaryGranularity,
)

# Re-export exceptions
from app.ai.exceptions import (
    AIContextError,
    AIContextModelError,
    AIContextValidationError,
    AIError,
    AIPersistenceError,
    AIProviderError,
    AIValidationError,
    PromptGenerationError,
)

# Re-export original models & new models
from app.ai.models import (
    AIAnalysis,
    AIContext,
    AIContextResult,
    AIMetadata,
    AIRecommendation,
    AIRequest,
    AIResult,
    AIUsageStatistics,
    ContextSection,
    PromptContext,
    RepositoryContext,
    SymbolContext,
)

# Re-export original builders/composer/cache
from app.ai.context_builder import AIContextBuilder as OriginalAIContextBuilder
from app.ai.repository_context import RepositoryContextBuilder
from app.ai.symbol_context import SymbolContextBuilder
from app.ai.context_composer import AIContextComposer
from app.ai.cache import ContextLookupCache

# Re-export new interfaces
from app.ai.interfaces import (
    AIAnalysisPersistence,
    AIContextBuilder,  # Sprint 30 AIContextBuilder interface
    LLMProvider,
    PromptBuilder,
    RecommendationGenerator,
)
from app.ai.context_aggregation import AIContextAggregationService
from app.ai.prompt_builder import PromptBuilderService

__all__ = [
    # Enums
    "ContextType",
    "ContextPriority",
    "SummaryGranularity",
    "AIAnalysisCategory",
    "AIProvider",
    "AIAnalysisStatus",
    "RecommendationPriority",
    "RecommendationCategory",
    "AIAnalysisType",
    # Exceptions
    "AIError",
    "AIValidationError",
    "AIProviderError",
    "AIContextError",
    "AIContextValidationError",
    "AIContextModelError",
    "AIPersistenceError",
    "PromptGenerationError",
    # Models
    "ContextSection",
    "SymbolContext",
    "RepositoryContext",
    "AIContextResult",
    "AIMetadata",
    "AIRequest",
    "AIContext",
    "PromptContext",
    "AIRecommendation",
    "AIUsageStatistics",
    "AIAnalysis",
    "AIResult",
    # Original interface
    "OriginalAIContextBuilder",
    # Repository context builders
    "RepositoryContextBuilder",
    "SymbolContextBuilder",
    "AIContextComposer",
    "ContextLookupCache",
    # New interfaces
    "AIContextBuilder",
    "PromptBuilder",
    "LLMProvider",
    "RecommendationGenerator",
    "AIAnalysisPersistence",
    # New services
    "AIContextAggregationService",
    "PromptBuilderService",
]
