"""CodeAtlas static quality rules package.

Provides Quality Rules Engine, RuleRegistry, BaseRule interface, and concrete
quality rule implementations.
"""

from app.analyzer.rules.base import BaseRule
from app.analyzer.rules.duplicate_exports import DuplicateExportsRule
from app.analyzer.rules.duplicate_imports import DuplicateImportsRule
from app.analyzer.rules.engine import RuleEngine
from app.analyzer.rules.exceptions import RuleEngineError, RuleError
from app.analyzer.rules.models import Diagnostic, Severity
from app.analyzer.rules.registry import RuleRegistry
from app.analyzer.rules.self_dependencies import SelfDependencyRule
from app.analyzer.rules.unresolved_calls import UnresolvedCallsRule
from app.analyzer.rules.unresolved_symbols import UnresolvedSymbolsRule
from app.analyzer.rules.unused_imports import UnusedImportsRule
from app.analyzer.rules.unused_symbols import UnusedSymbolsRule

__all__ = [
    # Re-exported Models
    "Diagnostic",
    "Severity",
    # Exceptions
    "RuleError",
    "RuleEngineError",
    # Base Interface, Registry & Engine
    "BaseRule",
    "RuleRegistry",
    "RuleEngine",
    # Concrete Rules
    "UnusedSymbolsRule",
    "UnusedImportsRule",
    "DuplicateImportsRule",
    "DuplicateExportsRule",
    "UnresolvedSymbolsRule",
    "UnresolvedCallsRule",
    "SelfDependencyRule",
]
