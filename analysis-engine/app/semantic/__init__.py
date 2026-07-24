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
from app.semantic.scope import ScopeNode
from app.semantic.scope_manager import ScopeManager
from app.semantic.symbol_table import SymbolTable
from app.semantic.reference_resolver import ReferenceResolver
from app.semantic.type_metadata import (
    TypeReference,
    TypeParameter,
    InheritanceInfo,
    DecoratorInfo,
    ModifierInfo,
    ParameterInfo,
    MethodSignature,
    PropertySignature,
    TypeMetadataExtractor,
)

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
    # Scope resolution classes
    "ScopeNode",
    "ScopeManager",
    # Symbol table engine
    "SymbolTable",
    # Reference resolution engine
    "ReferenceResolver",
    # Type metadata models & service
    "TypeReference",
    "TypeParameter",
    "InheritanceInfo",
    "DecoratorInfo",
    "ModifierInfo",
    "ParameterInfo",
    "MethodSignature",
    "PropertySignature",
    "TypeMetadataExtractor",
]
