"""CodeAtlas Architecture Analysis domain package."""

from app.architecture_analysis.enums import ArchitectureRuleType, ArchitectureSeverity
from app.architecture_analysis.exceptions import (
    ArchitectureAnalysisError,
    ArchitectureRuleError,
    ArchitectureRegistryError,
)
from app.architecture_analysis.models import ArchitectureIssue, ArchitectureReport, ArchitectureSummary
from app.architecture_analysis.analyzer import ArchitectureAnalyzer
from app.architecture_analysis.rule import ArchitectureRule
from app.architecture_analysis.registry import ArchitectureRuleRegistry
from app.architecture_analysis.engine import ArchitectureRuleEngine
from app.architecture_analysis.rules.circular_dependency import CircularDependencyRule
from app.architecture_analysis.rules.dependency_chain import DependencyChainRule
from app.architecture_analysis.semantic_context import ArchitectureSemanticContext
from app.architecture_analysis.semantic_rules import SemanticArchitectureRule
from app.architecture_analysis.context_builder import ArchitectureAIContextBuilder

__all__ = [
    "ArchitectureRuleType",
    "ArchitectureSeverity",
    "ArchitectureAnalysisError",
    "ArchitectureRuleError",
    "ArchitectureRegistryError",
    "ArchitectureIssue",
    "ArchitectureReport",
    "ArchitectureSummary",
    "ArchitectureAnalyzer",
    "ArchitectureRule",
    "ArchitectureRuleRegistry",
    "ArchitectureRuleEngine",
    "CircularDependencyRule",
    "DependencyChainRule",
    "ArchitectureSemanticContext",
    "SemanticArchitectureRule",
    "ArchitectureAIContextBuilder",
]
