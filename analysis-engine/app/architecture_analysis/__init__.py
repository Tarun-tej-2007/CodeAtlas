"""CodeAtlas Architecture Analysis domain package."""

from app.architecture_analysis.enums import ArchitectureRuleType, ArchitectureSeverity
from app.architecture_analysis.exceptions import ArchitectureAnalysisError, ArchitectureRuleError
from app.architecture_analysis.models import ArchitectureIssue, ArchitectureReport, ArchitectureSummary
from app.architecture_analysis.analyzer import ArchitectureAnalyzer

__all__ = [
    "ArchitectureRuleType",
    "ArchitectureSeverity",
    "ArchitectureAnalysisError",
    "ArchitectureRuleError",
    "ArchitectureIssue",
    "ArchitectureReport",
    "ArchitectureSummary",
    "ArchitectureAnalyzer",
]
