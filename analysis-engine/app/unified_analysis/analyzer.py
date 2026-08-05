"""Unified Analysis Analyzer Interface Module."""

from abc import ABC, abstractmethod
from typing import Any

from app.unified_analysis.models import UnifiedAnalysisReport


class UnifiedAnalysisAnalyzer(ABC):
    """Abstract base class establishing the contract for Unified codebase analyzers."""

    @abstractmethod
    def analyze(self, *, project_name: str, context: Any, **kwargs) -> UnifiedAnalysisReport:
        """Executes unified aggregation analysis and generates a UnifiedAnalysisReport.

        Args:
            project_name: Name identifier of the target project workspace.
            context: System context properties containing input components.

        Returns:
            A UnifiedAnalysisReport aggregate collection.
        """
        pass
