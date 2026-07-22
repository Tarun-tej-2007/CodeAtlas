"""Semantic analysis package.

Provides abstractions, models, enums, exceptions, and analyzer contracts
for codebase semantic symbol extraction and cross-reference resolution.
"""

from app.semantic.enums import (
    SymbolKind,
    ScopeKind,
    ReferenceKind,
    VisibilityKind,
)
from app.semantic.exceptions import (
    SemanticError,
    SemanticAnalysisError,
    SemanticModelError,
    SemanticResolutionError,
)
from app.semantic.models import (
    Location,
    SemanticSymbol,
    SemanticReference,
    SemanticScope,
    SemanticResult,
)
from app.semantic.analyzer import SemanticAnalyzer

__all__ = [
    # Enums
    "SymbolKind",
    "ScopeKind",
    "ReferenceKind",
    "VisibilityKind",
    # Exceptions
    "SemanticError",
    "SemanticAnalysisError",
    "SemanticModelError",
    "SemanticResolutionError",
    # Models
    "Location",
    "SemanticSymbol",
    "SemanticReference",
    "SemanticScope",
    "SemanticResult",
    # Interfaces
    "SemanticAnalyzer",
]
