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
]
