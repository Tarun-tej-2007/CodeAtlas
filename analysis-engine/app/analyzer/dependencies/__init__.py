"""CodeAtlas dependency analysis package.

Provides dependency relationship models, exception classes, DependencyBuilder,
and DependencyAnalyzer infrastructure.
"""

from app.analyzer.dependencies.analyzer import DependencyAnalyzer
from app.analyzer.dependencies.builder import DependencyBuilder
from app.analyzer.dependencies.exceptions import (
    DependencyAnalysisError,
    DependencyError,
)
from app.analyzer.dependencies.models import (
    Dependency,
    DependencyKind,
    DependencyResult,
    ModuleDependency,
)

__all__ = [
    # Enums & Domain Models
    "DependencyKind",
    "Dependency",
    "ModuleDependency",
    "DependencyResult",
    # Exceptions
    "DependencyError",
    "DependencyAnalysisError",
    # Builder & Analyzer
    "DependencyBuilder",
    "DependencyAnalyzer",
]
