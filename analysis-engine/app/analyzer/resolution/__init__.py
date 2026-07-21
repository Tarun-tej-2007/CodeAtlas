"""CodeAtlas intra-file symbol resolution package.

Provides domain models, Scope hierarchy manager, ResolutionVisitor, SymbolResolver,
and exception classes for intra-file symbol resolution.
"""

from app.analyzer.resolution.exceptions import ResolutionError
from app.analyzer.resolution.models import ResolutionResult, ResolvedReference
from app.analyzer.resolution.resolver import SymbolResolver
from app.analyzer.resolution.scope import Scope
from app.analyzer.resolution.visitor import ResolutionVisitor

__all__ = [
    # Data Models
    "ResolvedReference",
    "ResolutionResult",
    # Scope Management
    "Scope",
    # Exceptions
    "ResolutionError",
    # Visitor & Resolver
    "ResolutionVisitor",
    "SymbolResolver",
]
