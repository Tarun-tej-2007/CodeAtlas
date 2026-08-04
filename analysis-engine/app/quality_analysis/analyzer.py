"""Quality Analyzer Abstract Interface module."""

from abc import ABC, abstractmethod

from app.quality_analysis.models import QualityReport


class QualityAnalyzer(ABC):
    """Abstract base class defining the contract for codebase quality analyzers."""

    @abstractmethod
    def analyze(self, *args, **kwargs) -> QualityReport:
        """Executes software quality analysis and compiles a structured QualityReport."""
        pass
