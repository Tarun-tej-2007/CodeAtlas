"""CodeAtlas AI Context Analysis package.

Establishes structural enums, custom exceptions, model definitions, and pipeline
interfaces for constructing AI context packages.
"""

from app.ai.enums import (
    ContextType,
    ContextPriority,
    SummaryGranularity,
    AIAnalysisCategory,
)
from app.ai.exceptions import (
    AIContextError,
    AIContextValidationError,
    AIContextModelError,
)
from app.ai.models import (
    ContextSection,
    SymbolContext,
    RepositoryContext,
    AIContextResult,
)
from app.ai.context_builder import AIContextBuilder
from app.ai.repository_context import RepositoryContextBuilder
from app.ai.symbol_context import SymbolContextBuilder

__all__ = [
    # Enums
    "ContextType",
    "ContextPriority",
    "SummaryGranularity",
    "AIAnalysisCategory",
    # Exceptions
    "AIContextError",
    "AIContextValidationError",
    "AIContextModelError",
    # Models
    "ContextSection",
    "SymbolContext",
    "RepositoryContext",
    "AIContextResult",
    # Builder Abstract Interface
    "AIContextBuilder",
    # Repository Context Builder
    "RepositoryContextBuilder",
    # Symbol Context Builder
    "SymbolContextBuilder",
]
