"""Architecture Analysis Analyzer Interface module.

Defines the abstract interface for all Architecture Analyzers.
"""

from abc import ABC, abstractmethod

from app.graph import DependencyGraph
from app.architecture.models import ArchitectureAnalysisResult


class ArchitectureAnalyzer(ABC):
    """Abstract interface defining the execution contract for architectural analysis components."""

    @abstractmethod
    def analyze(self, graph: DependencyGraph) -> ArchitectureAnalysisResult:
        """Runs architectural checks, smells detection, layering and metric calculation.

        Args:
            graph: The DependencyGraph instance to analyze.

        Returns:
            An immutable ArchitectureAnalysisResult instance.
        """
        pass
